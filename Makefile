BUILD_DIR          = _build
BUNDLE_NAME        = mist
WORK_DIR           = $(BUILD_DIR)/$(BUNDLE_NAME)
SRC_FILES          = $(wildcard bin/*) $(wildcard commands/*) $(wildcard mist/*)

.PHONY: make-bundle validate-config

all: make-bundle

clean:
	rm -rf $(BUNDLE_NAME).cog _build

make-bundle: manifest.json validate-config
	mkdir -p $(WORK_DIR)
	cp manifest.json config.json $(WORK_DIR)
	cp -R bin $(WORK_DIR)
	cp -R commands $(WORK_DIR)
	cp -R mist $(WORK_DIR)
	cd $(BUILD_DIR) && zip -r $(BUNDLE_NAME).cog $(BUNDLE_NAME)
	mv $(BUILD_DIR)/$(BUNDLE_NAME).cog .

validate-config:
	@scripts/validate.py

manifest.json: $(SRC_FILES)
	scripts/package.py
