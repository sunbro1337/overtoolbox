#!python

import argparse
import getpass
import os
import shlex
import shutil
import sys
import traceback

import pysvn

import constants

R_KEEP = 0
R_DONE = 1
R_FAIL = 2
R_FAILKEEP = 3

REBASE_DIRECTORY = '.svn_rebase'
COMMANDS_FILE = os.path.join(REBASE_DIRECTORY, 'commands.todo')
ORIGINAL_COMMANDS_FILE = os.path.join(REBASE_DIRECTORY, 'commands.original')

COMMIT_MESSAGE = None

def main():
	parser = argparse.ArgumentParser(
		description='Execute a command list'
	)

	parser.add_argument('command_list',
				type=argparse.FileType('r'),
				help='A file with command list to execute',
				nargs='?')

	parser.add_argument('--continue',
				action='store_true',
				help='Continue an interrupted rebase process')

	parser.add_argument('-u', '--username',
			type=str,
			default=getpass.getuser(),
			help='A username to use for SVN access')
	parser.add_argument('-p', '--password',
			type=str,
			help='A password to use for SVN access')

	parser.add_argument('-P', '--prompt',
			action='store_true',
			help='Prompt for a psssword in secure matter')

	parser.add_argument('--cwd',
						type=str,
						metavar='CWD',
						default='',
						help='A current working directory (default: autodetect)')

	args = parser.parse_args()

	if args.command_list and getattr(args, 'continue', False):
		parser.error("You may only give a new command list"
						" or use --continue")
	
	if not args.command_list and not getattr(args, 'continue', False):
		parser.error("You should either give a new command list or"
						" or use --continue")

	if not args.command_list and not os.path.exists(REBASE_DIRECTORY):
		parser.error("Continue requested, but there is no {0}"
				" directory".format(REBASE_DIRECTORY))

	if args.command_list and os.path.exists(REBASE_DIRECTORY):
		parser.error("{0} still exists, probably another rebase"
				" already in progress. If it's not the case,"
				" please remove the directory"
				.format(REBASE_DIRECTORY))

	if args.command_list:
		commands = init_processing(args.command_list)
		args.command_list.close()
	else:
		commands = continue_processing()

	client = init_client(args.username, args.password, args.prompt)

	success = execute_commands(client, args.username, commands)

	if success:
		cleanup_processing()
		return 0
	else:
		return 1

def init_processing(commands_list):
	os.mkdir(REBASE_DIRECTORY)

	shutil.copyfile(commands_list.name, ORIGINAL_COMMANDS_FILE)
	shutil.copyfile(commands_list.name, COMMANDS_FILE)

	return read_commands(commands_list)

def continue_processing():
	fd = open(COMMANDS_FILE, 'r')
	commands = read_commands(fd)
	fd.close()

	return commands

def cleanup_processing():
	shutil.rmtree(REBASE_DIRECTORY)

def init_client(username, password, prompt):
	client = pysvn.Client()

	save_password = True
	if password is None and prompt:
		save_password = False
		password = getpass.getpass()

	def get_login(realm, username, may_save):
		return password is not None,	\
			username, password,	\
			may_save and save_password
	
	def get_log_message():
		global COMMIT_MESSAGE

		if COMMIT_MESSAGE is None:
			return False, None
	
		message = COMMIT_MESSAGE
		COMMIT_MESSAGE = None

		return True, message

	def get_trust(trust_dict):
		return True, 5, True

	client.callback_get_login = get_login
	client.callback_get_log_message = get_log_message
	client.callback_ssl_server_trust_prompt = get_trust
	return client


def super_shlex_split(line):
	lexer = shlex.shlex(line, posix=True)
	lexer.commenters = ";"
	lexer.whitespace_split = True

	return list(lexer)


def read_commands(commands_file):
	commands = []

	for lineno, line in enumerate(commands_file.readlines()):
		try:
			args = super_shlex_split(line)
		except ValueError:
			print "Error at", lineno
			raise

		if len(args) == 0:
			continue

		command = args.pop(0)

		commands.append((command, args))
	
	return commands

def execute_commands(client, username, commands):
	success = False

	data = Data()
	data.username = username
	commands_left = commands[:]
	i = 0

	for name, args in commands:
		try:
			command = globals()['command_' + name]
			result, additions = command(client, data, *args)
		except:
			traceback.print_exc()

			result = R_FAILKEEP
			additions = None

		if result in (R_DONE, R_FAIL):
			commands_left.pop(i)

		if additions is not None:
			commands_left = commands_left[:i]	\
					+ additions		\
					+ commands_left[i:]

			i += len(additions)
		elif result in (R_FAIL, R_FAILKEEP):
			if name != "cleanup":
				commands_left.insert(i, ("cleanup", []))

			if data.current is not None:
				commands_left.insert(i + 1,
						("switch", [data.current]))

		if result in (R_KEEP, R_FAILKEEP):
			i += 1

		write_commands_list(commands_left)

		if result in (R_FAIL, R_FAILKEEP):
			break
	else:
		success = True

	return success

def write_commands_list(commands):
	fd = open(COMMANDS_FILE, 'w')
	
	for command, args in commands:
		components = [command]

		for arg in args:
			if not arg.isalnum():
				arg = arg.replace(r'"', r'\"')
				arg = '"' + arg + '"'

			components.append(arg)

		fd.write(" ".join(components) + "\n")
	
	fd.close()

def get_current_revision(client):
	return client.info(".").revision.number

def set_log_message(message):
	global COMMIT_MESSAGE
	COMMIT_MESSAGE = message

class Data():
	def __init__(self):
		self.base = None
		self.current = None
		self.username = None
	
	def uri(self, branch):
		return self.base + "/" + branch

def command_cleanup(client, data):
	print ">>> Cleanup"
	print "\t>>> Rollback any open transaction"
	client.cleanup(".")

	print "\t>>> Revert all changes"
	client.revert(".", depth=pysvn.depth.infinity)

	print "\t>>> Remove unversioned and ignored files"
	status = client.status(".", ignore=True, depth=pysvn.depth.infinity)

	to_remove = []

	for stat in status:
		if stat.is_versioned:
			continue

		if stat.text_status not in (pysvn.wc_status_kind.unversioned,
						pysvn.wc_status_kind.ignored):
			continue

		if stat.path == REBASE_DIRECTORY:
			continue

		if stat.path == "mobile_svn_rebase.exe":
			continue

		if stat.path == "rebase.data":
			continue

		if stat.path == "rebase_data_trash.txt":
			continue

		print "\t\t>>> Remove {0}".format(stat.path)

		if os.path.isdir(stat.path):
			shutil.rmtree(stat.path)
		else:
			os.remove(stat.path)
	
	return R_DONE, None

def command_base(client, data, base):
	data.base = base
	return R_KEEP, None

def command_current(client, data, branch):
	data.current = branch
	return R_KEEP, None

def command_remove(client, data, branch, message):
	print ">>> Remove {0}".format(branch)

	set_log_message(message)
	client.remove(data.uri(branch))
	return R_DONE, None

def command_copy(client, data, source, destination, message):
	print ">>> Copy {0} -> {1}".format(source, destination)
	
	source, rev = source.split('@')
	
	if rev == "HEAD":
		rev = pysvn.Revision(pysvn.opt_revision_kind.head)
	else:
		rev = pysvn.Revision(pysvn.opt_revision_kind.number, rev)

	set_log_message(message)
	client.copy(data.uri(source),
				data.uri(destination),
				src_revision=rev)
			
	return R_DONE, None

def command_switch(client, data, branch):
	print ">>> Switch to {0}".format(branch)

	client.switch(".", data.uri(branch),
			depth=pysvn.depth.infinity)
	data.current = branch
	return R_DONE, [("current", [branch])]

def command_merge(client, data, source_revision, author, first_line):
	source, revision = source_revision.split('@')
	
	print '>>> Merge revision {0} by {1} "{2}"'\
				.format(revision, author, first_line)

	print "\t>>> Merge {0}@{1}".format(source, revision)

	revision = int(revision)

	current = pysvn.Revision(pysvn.opt_revision_kind.number, revision)
	previous = pysvn.Revision(pysvn.opt_revision_kind.number, revision - 1)

	client.merge(data.uri(source), previous,
					data.uri(source), current,
					".", notice_ancestry=False)

	return try_commit_merge(client, data, source, revision)

def try_commit_merge(client, data, source, revision):
	print "\t>>> Retrieving a full commit message"

	current = pysvn.Revision(pysvn.opt_revision_kind.number, revision)

	log = client.log(data.uri(source), current, current,
						peg_revision=current)
	assert(len(log) == 1)
	log = log[0]
	
	message = log.message	
	original_author = constants.get_original_author(message)
	
	if original_author is None:
		message += "\n\n" + constants.ORIGINAL_REVISION_PREFIX + str(revision)
		message += "\n" + constants.ORIGINAL_AUTHOR_PREFIX + log.author
	
	message += "\n" + constants.REBASED_BY_PREFIX + data.username

	try:
		print "\t>>> Commit"
		client.checkin('.', message, depth=pysvn.depth.infinity)
	except pysvn.ClientError as e:
		sys.stderr.write(str(e) + "\n")

		return R_FAIL, [("commit_if_rev", [
			str(get_current_revision(client)),
			source + "@" + str(revision)
		])]
	
	return update_after_merge(client)

def update_after_merge(client):
	print "\t>>> Update"
	client.update('.', recurse=True)

	return R_DONE, None

def command_commit_if_rev(client, data, guard, source_revision):
	print ">>> Trying to commit previous merge"
	
	current = get_current_revision(client)
	guard = int(guard)

	if current > guard:
		print "\t>>> Something is already commited. Skipping"
		return update_after_merge(client)
		
	source, revision = source_revision.split('@')
	
	return try_commit_merge(client, data, source, int(revision))

def command_reintegrate_and_add_to_contents_txt(client, data, branch, message):
	print ">>> Reintegrating {0}".format(branch)

	print "\t>>> Merging {0}".format(branch)

	client.merge_reintegrate(data.uri(branch),
				pysvn.Revision(pysvn.opt_revision_kind.head),
				".")

	print "\t>>> Recording branch into contents.txt"

	fd = open("contents.txt", "a")
	fd.write(branch + "\n")
	fd.close()

	client.add("contents.txt", force=True, ignore=False, recurse=False)

	print "\t>>> Comitting"

	client.checkin('.', message, depth=pysvn.depth.infinity)

	return R_DONE, None


if __name__ == "__main__":
	retval = main()
	sys.exit(retval)
