for remote in `git branch -r | grep -v /HEAD`; do git checkout --track $remote ; done
