# Select explicit local prerequisites

For this public candidate, follow [acquisition and installation](installation-unverified.md)
and [reproduction](reproduction.md). Those instructions select explicit interpreter,
PowerShell, font and optional rendering-tool paths within the reader's environment.
No private machine-locator JavaScript Object Notation (JSON) file, owner-specific absolute path or private helper is
needed to perform the documented project tasks.

The historical R6/R7 reader validation used an already installed environment and a
separately supplied locator. Its hashes established that particular machine's
inputs; they are not expected hashes for every reader's executable or font files.
The [coverage record](reader-acceptance.md) retains this distinction. Matching
Python/package version numbers does not prove identical interpreter builds,
fonts, dependency bytes or runtime behaviour.

Use a normal non-administrator Windows account and PowerShell 7.2 or newer
(the specified reproducible acquisition target is 7.6.9). The existing controlled
reader launcher verifies the ordinary-user context before business execution.
Do not elevate or remove its checks to turn a refused run into a pass. Preserve
failed outputs and resolve the affected prerequisite before a separate attempt.

New tool locations and observed versions belong in the reader's local execution
record. Keep logs containing machine paths or user identifiers out of public
commits. The engineering candidate itself does not install software or certify a
fresh environment.
