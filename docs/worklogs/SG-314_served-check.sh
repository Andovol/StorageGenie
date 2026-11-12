cd /app/static/assets || exit 1
echo "css_files: $(ls *.css | tr '\n' ' ')"
echo "js_files: $(ls *.js | tr '\n' ' ')"
for s in 'Checking the file' 'Tidying the details' 'Looking for duplicates' 'Your review' 'Saving' 'nav-menu-toggle' 'evidence state' 'per-press'; do printf 'js[%s]=' "$s"; cat *.js | grep -o -F "$s" | wc -l; done
printf 'css[--paper]='; cat *.css | grep -o -F -- '--paper' | wc -l
echo "css_paper_rules:"; cat *.css | grep -o '[^{}]*{[^{}]*--paper[^{}]*}'
echo "css_font_rules_controls:"; cat *.css | grep -o '[^{}]*{[^{}]*font-family[^{}]*}' | grep -i -E 'button|input|select|textarea|control'
echo "css_woff2_refs:"; cat *.css | grep -o '[A-Za-z0-9_./-]*\.woff2' | sort -u
