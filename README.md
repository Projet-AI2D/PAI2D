# PAI2D

on a trouvé les instances ici : https://github.com/PrefLib/PrefLib-Data/blob/main/datasets/00009%20-%20agh/00009-00000002.soc

recuperer les fichiers .soc

curl -s https://api.github.com/repos/PrefLib/PrefLib-Data/git/trees/main?recursive=1 | jq -r '.tree[] | select(.path | endswith(".soc")) | .path' | while IFS= read -r file; do     mkdir -p "$(dirname "$file")";      encoded_path=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$file");      curl -L --fail -o "$file"     "https://raw.githubusercontent.com/PrefLib/PrefLib-Data/main/$encoded_path"; done


nomFichier Nb_candidats 3/4Maj+ProgDyn CCE+ProgDyn 3/4Maj+CCE+ProgDyn CCE+3/4Maj+ProgDyn ProgDyn 3/4Maj+PL CCE+PL 3/4Maj+CCE+PL CCE+3/4Maj+PL PL 
