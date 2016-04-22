BUILD_DIR          = _build
BUNDLE_NAME        = mist
WORK_DIR          := $(BUILD_DIR)/$(BUNDLE_NAME)
SRC_DIRS           = bin commands meta templates lib
SRC_FILES         := $(foreach dir, $(SRC_DIRS), $(wildcard $(dir)/*))
TAG                = cogcmd/mist:0.5

.PHONY: make-bundle validate-config

all: Makefile manifest.json config.yaml $(SRC_FILES)
	docker build -t $(TAG) .
