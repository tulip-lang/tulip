## Tulip packaging

Tulip packages are called "bulbs".  They are not hosted by any service - rather, the local installation tools will pull directly from git, using specially-formatted and signed tags.  The bulb *registry* (implementation tbd) will maintain mappings from user -> pubkey, and package-name -> (git-url, user).  Version releases will be represented by signed git tags (see `git tag -s`) of the format `vX.X.X`, where `X.X.X` is a semver version.  The local tools will consult with the registry to verify the signing against the user's registered public key.

Package dependencies will eventually be resolved to a single version per package, similar to bundler.  Tulip will admit multiple versions of a package in the runtime simultaneously, but only with hot code loading - at boot, there is exactly one version of each package, and at any given time, there is a canonical "current" version of the package. This state is maintained by the code server.

To facilitate dependency resolution, dependencies should be specified with fuzzy version numbers, of the two following forms:

* `1.2+` (admits `1.2.x`, `1.3.x`, `1.9.x`, but not `1.1.x` or `2.x`)
* `1.2.3-5` (admits `1.2.3`, `1.2.4`, or `1.2.5` and no others)

The fuzzy specifier may appear in major, minor, or patch version fields.

After resolution, the resolved versions, the git urls, and a hash of the git tag and associated tree will all be saved to a lockfile.  For deployable projects (as opposed to publishable packages), these files should be checked in to avoid shenanigans with deleting and re-publishing tags and the like.
