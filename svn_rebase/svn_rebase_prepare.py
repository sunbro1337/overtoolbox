#!python

import argparse
import getpass
import sys
import os

import pysvn

import constants

def main():
	parser = argparse.ArgumentParser(
		description='Prepare a command list for a svn_rebase script'
	)

	parser.add_argument('branch',
				type=str,
				help='A branch to commit to')

	parser.add_argument('--source',
				type=str,
				help='A branch to take changes from'\
				' (default: same as branch)')

	parser.add_argument('--upstream',
				type=str,
				default='main',
				help='A branch to base a new branch on'\
				' (default: main)')
				
	parser.add_argument('--onto',
				type=str,
				help='A branch to base a new branch on'\
				' (default: <upstream>)')
				
	parser.add_argument('--onto-revision',
				type=int,
				default=-1,
				help='A revision of the base to copy a new branch from'\
				' (default: HEAD)')

	parser.add_argument('-o', '--output',
			type=argparse.FileType('w'),
			default=sys.stdout,
			metavar='FILE',
			help='A file to output commands into (default: stdout)')

	parser.add_argument('--repo',
			type=str,
			metavar='URI',
			default='',
			help='A SVN repo uri (default: autodetect)')

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

	parser.add_argument('--first-revision',
			type=int,
			default=-1,
			help='Repeat changes starting with the given revision'
							' (default: auto)')

	parser.add_argument('--top-revision',
			type=int,
			default=-1,
			help='Look for a branch that ends at that revision'
							' (default: HEAD)')

	parser.add_argument('--rebuild-main',
			action='store_true',
			help='Rebuild a main-alike branch by rebasing all'
				' feature-branches based on the batch and'
				' merging them back'
				' (require contents.txt in the brach root)')

	parser.add_argument('--cwd',
						type=str,
						metavar='CWD',
						default='',
						help='A current working directory (default: autodetect)')

	args = parser.parse_args()

	if args.rebuild_main and args.first_revision >= 0:
		parser.error('--recursive option implies automatic'\
					' first-revision detection')
	
	client = init_client(args.username, args.password, args.prompt)

	if len(args.repo) == 0:
		if len(args.cwd) == 0:
			args.repo = get_working_copy_repo(client)
		else:
			args.repo = get_working_copy_repo(client, args.cwd)

	output_header(args.output)
	output_set_base(args.output, args.repo)
	
	if not args.onto:
		args.onto = args.upstream

	if not args.rebuild_main:
		output_branch(args.output, client, args.repo,
				args.branch, args.source, args.upstream,
				args.onto, args.onto_revision,
				args.first_revision, args.top_revision)
		return 0

	output_branch_rebuild(args.output, client, args.repo,
				args.branch, args.source, args.upstream,
				args.onto, args.onto_revision,
				args.first_revision, args.top_revision)

	return 0


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

	def get_trust(trust_dict):
		return True, trust_dict['failures'], True

	client.callback_get_login = get_login
	client.callback_ssl_server_trust_prompt = get_trust

	return client


def get_working_copy_repo(client, cwd=None):
	if cwd:
		info = client.info(cwd)
	else:
		info = client.info(os.getcwd())
	return info.repos


def check_branch_exists(client, base, branch, top):
	try:
		revision = get_revision_or_head(top)
		top = get_revision_or_undef(top)
		client.list(base + "/" + branch,
				depth=pysvn.depth.empty,
				revision=revision,
				peg_revision=top)
		return True
	except pysvn.ClientError:
		return False


def output_branch(fd, client, base, branch, source, upstream, onto, onto_rev, start, top):
	if check_branch_exists(client, base, branch, top):
		output_branch_remove(fd, branch)
		output_branch_copy(fd, branch, onto, onto_rev)
	else:
		output_branch_copy(fd, branch, onto, onto_rev)

	if source is None:
		source = branch

	output_cleanup(fd)
	output_switch(fd, branch)

	output_branch_commits(fd, client, base, source, upstream, start, top)


def output_branch_rebuild(fd, client, base, branch, source, upstream, outo, onto_rev, start, top):
	if check_branch_exists(client, base, branch, top):
		output_branch_remove(fd, branch)
		output_branch_copy(fd, branch, outo, onto_rev)
	else:
		output_branch_copy(fd, branch, outo, onto_rev)
	
	branches = read_contents_list(client, base, branch, top)

	for subbranch, upstream in branches:
		output_branch(fd, client, base, subbranch, subbranch, upstream, branch, -1, top)

		output_switch(fd, branch)
		output_reintegrate_and_add_to_contents_txt(fd, subbranch)


def read_contents_list(client, base, branch, top):
	contents = read_svn_file(client, base, branch, top, "contents.txt")

	branches = []

	for line in contents.split("\n"):
		line = line.split("#")[0].strip()

		if line == "":
			continue

		parts = line.split(':')
		subbranch = parts[0]
		upstream = parts[1] if len(parts) > 1 else branch

		if not check_branch_exists(client, base, subbranch, top):
			sys.stderr.write("Branch {0} do not exists!\n"
							.format(subbranch))
			sys.exit(1)

		branches.append((subbranch, upstream))

	return branches


def get_revision_or_undef(top):
	if top >= 0:
		return pysvn.Revision(pysvn.opt_revision_kind.number, top)
	else:
		return pysvn.Revision(pysvn.opt_revision_kind.unspecified)


def get_revision_or_head(top):
	if top >= 0:
		return pysvn.Revision(pysvn.opt_revision_kind.number, top)
	else:
		return pysvn.Revision(pysvn.opt_revision_kind.head)


def read_svn_file(client, base, branch, top, path):
	revision = get_revision_or_head(top)
	top = get_revision_or_undef(top)

	return client.cat(base + "/" + branch + "/" + path, revision, top)


def output_branch_commits(fd, client, base, source, upstream, start, top):
	stop_on_copy = False
	look_for_upstream = False

	if start < 0:
		start = 0
		stop_on_copy = True
		look_for_upstream = True

	if upstream[0] != "/":
		upstream = "/" + upstream
	
	end = get_revision_or_head(top)
	top = get_revision_or_undef(top)

	source_url = base + "/" + source

	start = pysvn.Revision(pysvn.opt_revision_kind.number, start)

	commits = []

	while True:
		messages = client.log(source_url, end, start,
				discover_changed_paths=look_for_upstream,
				strict_node_history=stop_on_copy,
				peg_revision=top)

		revision = 0

		for message in messages:
			if len(message.changed_paths) == 1:
				path = message.changed_paths[0]

				if path.copyfrom_path == upstream:
					look_for_upstream = False
					break

			first_line = message.message.split('\n')[0]
			
			author = constants.get_original_author(message.message)
			merge_status = constants.get_merge_status(message.message)
			
			if author is None:
				author = message.author

			revision = message.revision.number
			comment = first_line
			
			if merge_status is not None:
				comment += " # " + merge_status
			
			commits.append((revision, author, comment))

		end = pysvn.Revision(pysvn.opt_revision_kind.number,
							revision - 1)

		if not look_for_upstream:
			break
	
	commits.reverse()

	for revision, author, first_line in commits:
		output_merge(fd, source, revision, author, first_line)


def output_branch_remove(fd, branch):
	fd.write('remove {0} "Remove the branch for rebasing"\n'.format(branch))


def output_branch_copy(fd, branch, upstream, rev):
	if rev < 0:
		rev = "HEAD"
		
	fd.write('copy {0}@{1} {2} "Create a new branch from {0}"\n'
					.format(upstream, rev, branch))


def output_reintegrate_and_add_to_contents_txt(fd, branch):
	fd.write('reintegrate_and_add_to_contents_txt {0} "Merge {0}"\n'
							.format(branch))


def output_cleanup(fd):
	fd.write('cleanup\n')


def output_switch(fd, branch):
	fd.write('switch {0}\n'.format(branch))


def output_set_base(fd, base):
	fd.write('base {0}\n'.format(base))


def output_merge(fd, source, revision, author, message):
	message = message.replace('"', r'\"')
	fd.write('merge {0}@{1} {2} "{3}"\n'.format(source, revision, author, message))


def get_commit_line(rev):
	out, err = subprocess.Popen(["svn", "log", "-r", rev, source_path],
					stdout=subprocess.PIPE).communicate()
	lines = out.splitlines()

	for line in out.splitlines()[3:]:
		if not re.match('^\s*$', line):
			return line


def make_merge_data(rev):
	commit_line = get_commit_line(rev)

	sys.stdout.write('keep {rev:06d} {commit_line}\n'
					.format(rev=int(rev),
						commit_line=commit_line))


def output_header(fd):
	fd.write("""\
;;
;; SVN bulk merge-and-commit command set. Generated by {generator}
;;
;; See readme.txt somewhere near the script for a commands description
;;
;; Everything after the '#' sign is ignored.
;; Merge commit messages are mere convenience and do not affect anything
;;
""".format(generator=sys.argv[0]))


if __name__ == "__main__":
	retval = main()
	sys.exit(retval)
