When your solution is added to source control for the first time, the wizard creates a local repo and 
a twin on GitHub simultaneously. If a Git dropdown tab isn’t already visible on your menu bar, it 
automatically adds a tab to your menu bar. You administer and manage all things to do with version 
control and your repositories from the dropdown. The local Git repo and the remote repo on GitHub 
are intended to be operated as clones and kept regularly in sync with each other. 

Each time a local commit (matched by a Push to remote) is done, any modified/new files are saved 
locally on Git and remotely on GitHub. This means that your (hidden) .git file inside your VS 2022 
solution folder gets bigger and bigger as time goes by. It can grow from 20Mb to over 200Mb. This 
means that file-size related operations get slower and slower, including opening and closing the 
Solution, zipping the solution, and saving the zipped solution. The way to slim the repos back to 
their original size is to reinitialise them. Another reason to initialise them is if the repos 
somehow get irreversibly out of sync, or corrupted or need to be replaced from scratch from a 
previously saved zipped file of the solution.

The approach is to detach the solution from remote and local version control, then delete the 
repository on GitHub, then delete the git-related files that reside inside the solution folder, and 
then finally re-add the solution to source control. To do this, take the following steps:

Step 1:	Git>Manage Remotes>Remotes and manually delete the URLS linking the sln to GitHub.
Step 2:	Git>Settings>Source Control>Plug-in Selection and change selection from Git to none.
Step 3:	In the solution folder, delete the files .git,.gitattributes, and .gitignore.
Step 4:	On the GitHub website, select the repository, then top tab >Settings then scroll down >Delete.
Step 5:	Back in VS2022, go Tools>Options>Source Control>Plug-in selection and change to Git.
Step 6:	Go Git>Create Git repository…
Step 7:	The create wizard pops up. Go ahead and create your fresh pair of repositories.
Step 8:	Populate the new repositories. Go Git>Commit or stash>Commit all and push.

Hey presto. Job done.
31st April 2024

