BUILD_DIR          = _build
BUNDLE_NAME        = mist
WORK_DIR           = $(BUILD_DIR)/$(BUNDLE_NAME)
SRC_FILES          = $(wildcard bin/*) $(wildcard commands/*)

.PHONY: make-bundle

all: make-bundle

make-bundle: manifest.json
	mkdir -p $(WORK_DIR)
	cp manifest.json config.json $(WORK_DIR)
	cp -R bin $(WORK_DIR)
	cp -R commands $(WORK_DIR)
	cd $(BUILD_DIR) && zip -r $(BUNDLE_NAME).cog $(BUNDLE_NAME)
	mv $(BUILD_DIR)/$(BUNDLE_NAME).cog .

manifest.json: $(SRC_FILES)
	scripts/package.py
