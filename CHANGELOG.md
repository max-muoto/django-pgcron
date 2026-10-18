## 0.2.0 (Unreleased)

### Breaking changes

- Drop Python 3.10 support. Python 3.11 or newer is now required.

### Compatibility

- Extend the supported Python range through Python 3.15.
- Add compatibility coverage for Django 5.2 and 6.1, including their minimum
  PostgreSQL versions (14 and 15, respectively).
- Add PostgreSQL 18 support. Update the development database image to build
  pg_cron 1.6.8 while retaining PostgreSQL 17 as the local default.

### Fixes

- Raise a clear `TypeError` when `PGCRON_DATABASE` is not a string.
- Fix PostgreSQL extension builds by using the base image's matching LLVM toolchain.
- Fix documentation builds with the current mkdocstrings configuration format.

### Dependencies

- Update locked Django, sqlparse, and pytest versions to 5.2.18, 0.6.0, and 9.1.1
  to address dependency security advisories. The public Django requirement remains
  `django>=5.0.0`.

## 0.1.0 (2024-12-27)

#### Api-Break

  - Initial release of django-pgcron. [Max Muoto, 501111e]
