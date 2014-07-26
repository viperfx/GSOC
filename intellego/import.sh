yes 1 | amagama-manage dropdb -s en -s es
amagama-manage initdb -s en -s es
amagama-manage build_tmdb --verbose -s en -t es -i ../GaiaGlossary.tbx
amagama-manage build_tmdb --verbose -s en -t es -i logs/term_extraction_realign2.csv
yes 1 | amagama-manage deploy_db
