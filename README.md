#GSOC 2014
**Mozilla Intellego -- Terminology-driven automatic translation of web sites.**

You can view my progress on the project on this [blog](http://tharshan-gsoc.logdown.com)

##Components
| Name          | Path          | Description |
| -------------- | ------------- | ------------- |
| amaGama Server  | intellego/amagama/ | This contains the [amaGama](http://docs.translatehouse.org/projects/amagama/en/latest/) project with modifications. |
| Term Extraction Script  | intellego/term_extraction.py | Extracts bilingual terminology from a TMX file. |
| Import Script | intellego/import.sh | Shell script to delete and recreate the database with data. |
| Pathfix Script | intellego/pathfix.sh | Script to add the executables in the /bin folder the PATH. |
| Log files | intellego/logs/ | Various log files created through out the duration of the project. The CSV files contain the results of the term extraction script, which can be immported into the database. |
| NLTK align | intellego/align |  This contains the NLTK align module with some minor modifications. |
| Terminology File | memoire_en-US_es-ES.tmx | TMX file downloaded from the [Transvision](http://transvision.mozfr.org/downloads/) project.|

##Translation Interface
The final deliverable along with this project other than the command line script is a web interface to be able to connect all the work I have done. This web interface has a text area input to translate words individually and a URL input to translate web pages.

The amaGama project has been extended for our purposes. We chose to use amaGama because it had a way to store bilingual terminology along with a simple REST API to query the database. Detailed changes to the amaGama project can be viewed [here](https://github.com/viperfx/GSOC/commits/master/intellego/amagama). Initially the levenstein distance ranking done in `tmdb.py` was removed during the initial stages of the project. Now the `translate_unit` has been returned to the orginal version found in amaGama. The sensistivity of the ranking can be tuned through variables such as `MIN_SIMILARITY` found in `settings.py`.

![Test](http://cl.ly/image/2Y19130Z0o11/Screen%20Shot%202014-08-15%20at%2016.02.27.png)

amaGama has mostly remained unchanged and only used as an API to query the database. `views/web.py` contains Flask views for the web interface for the project, where the user can translate a piece of text or a web page.


##Setup Instructions
All the dependancies are included in the project. Using these steps, this project can be hosted on a server.
1. Clone the project
2. Create a virtualenv and `pip install intellego/requirements/recommended.txt`
3. Setup paths using `source intellego\pathfix.sh`
4. The project already has extracted terminology. You can use the provided `import.sh` script to import them or modify it to import another terminology file you may have created using the script.
5. This project required the use of a postgres database. Make sure the database is setup for amaGama. Instructions can be found [here](http://docs.translatehouse.org/projects/amagama/en/latest/installation.html).
5. The application can be run using `python amagama/application.py` inside the intellego directory.

##Terminology Extraction Script
This script takes a TMX files as an input and can create various outputs based on the commmand line options given. The script uses NLTK and Pattern to analyse the contents of the TMX file to build up a corpus of aligned sentenences. The IBMModel2 in the NLTK Align module is used to build up a model with the aligned corpus. The model contains a mapping of source words to target words with a precision value. The precision value ranges from 0.0 to 1.0, the higher the better.
```
Usage: term_extraction.py [OPTIONS]

Options:
  --load TEXT  Specifiy a model to save.
  --train      Train the model. If this flag is not set, then it will load a
               saved model.
  --debug      Print the debug json file. Pipe the output to a file using this
               flag.
  --csv        Print the translated pairs in CSV format. Pipe the output to a
               file using this flag.
  --help       Show this message and exit.
```
| Log File          | Purpose          |
| ----------------- | ---------------- |
| term_extraction_realign2.csv | The latest result of the term extraction tool. |
| term_extraction_realign.csv | The term extraction result that includes only the POS tagger. |
| debug_corpus.json | This JSON file contains bilingual terminology with metadata that would help to quickly cross check translations. It includes the TUID from the TMX file for each source word. |
