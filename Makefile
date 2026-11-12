# Automatically find all inventory names where an 'inventory' file exists inside inventories/
INVENTORIES := $(patsubst inventories/%/inventory,%,$(wildcard inventories/*/inventory))

# Mark these targets as phony so Make doesn't look for files named after them
.PHONY: all $(INVENTORIES)

# Default action when running just 'make'
default:
	@echo "Usage: make <inventory-name>"
	@echo "Available inventories: $(INVENTORIES)"

# Defaults to empty; pass ARGS="..." to forward any flags to ansible-playbook
ARGS ?=

# Dynamic rule matching any discovered inventory name
$(INVENTORIES):
	ansible-playbook -i inventories/$@/inventory playbook.yml $(ARGS)

