# Diary

This project is mostly personal at this point but could possibly be used by anyone.

What each script does:

* `gen.py`
	+ Reads sqlite3 DB and generates pages from the templates
		-puts them in the output directory.
* `grab.py`
	+ Logs into email inbox using config credentials.
	+ Finds all emails recieved from self with the proper title.
	+ Adds these emails to the sqlite3 DB.
* `upload.sh`
	+ Runs `grab.py`
	+ Uploads the contents of `output/` to neocities.
