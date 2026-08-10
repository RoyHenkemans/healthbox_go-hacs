# Home Assistant Core proposal plan

This repository is the feature-complete custom integration. A first Home
Assistant Core pull request should be intentionally smaller.

## Required release prerequisites

1. Move `library/` to its own public repository with issues enabled.
2. Keep the MIT license and publish both source distribution and wheel from the
   included public trusted-publishing workflow.
3. Tag `v0.1.0`; the PyPI version and tag must correspond exactly.
4. Confirm the final PyPI name and update `manifest.json` if it differs.
5. Add Renson Healthbox Go brand assets through `home-assistant/brands`.
6. Create Home Assistant documentation with installation and removal steps.

## Recommended first Core PR

Home Assistant asks new integration PRs to be minimal and normally limited to
one platform. Start with:

- config flow on host/IP, connection test and serial-number unique ID;
- config entry runtime data and coordinator;
- `sensor` platform only: temperature, humidity, CO2, VOC and ventilation;
- full config-flow and integration test coverage;
- one pinned release of the external Python library.

Leave the following out of that first Core PR and add them in follow-ups:

- fan, number, select, switch, time, button and binary sensor platforms;
- diagnostics and diagnostic entities;
- custom actions;
- reconfigure flow;
- optional discovery.

The full HACS integration can continue to expose those features. Maintain a
small Core branch or extract the initial files when preparing the PR.

## Bronze checklist status

- UI config flow: implemented
- Connection tested before configure: implemented
- Connection tested during setup: implemented
- Unique config entry by device serial: implemented
- Entity unique IDs and `has_entity_name`: implemented
- Runtime state in `ConfigEntry.runtime_data`: implemented
- Appropriate local polling coordinator: implemented (15 seconds)
- Standalone communication dependency: implemented in source; PyPI/public CI
  release still required
- Config-flow and integration test coverage: still required for the Core PR
- Brand assets: still required in `home-assistant/brands`
- Core documentation: still required in `home-assistant.io`

## Important distinction

Being structurally prepared is not the same as being eligible today. Core's
dependency-transparency rule has no exception: the library must actually be on
PyPI, built by public CI, and match a tagged public source release before the
integration PR is submitted.

