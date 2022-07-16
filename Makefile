pyinstaller-cli:
		pyinstaller -F shamela2epub/cli/app.py \
		--clean -y \
		--add-data="pyproject.toml:." \
		--add-data="shamela2epub/assets/styles.css:./shamela2epub/assets/" \
		--icon="shamela2epub/assets/books-duotone-128.png" \
		--windowed \
		-n shamela2epub
pyinstaller-gui:
		pyinstaller -F shamela2epub/gui/app.py \
		--clean -y \
		--add-data="pyproject.toml:." \
		--add-data="shamela2epub/assets:./shamela2epub/assets" \
		--add-data="shamela2epub/gui/ui.ui:./shamela2epub/gui/" \
		--icon="shamela2epub/assets/books-duotone-128.png" \
		--windowed \
		--hidden-import PyQt5.sip \
		-n shamela2epubgui
