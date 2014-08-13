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
