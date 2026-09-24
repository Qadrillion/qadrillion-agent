# Parcel ledger acceptance contract

This is a disposable native Android app with synthetic local data. No account,
network service or permission grant is needed. Package: `com.qadrillion.parcel`.

1. A clean install or explicit app-data reset starts at zero parcels and units.
2. Add parcel accepts whole-number quantities from 1 through 5, inclusive.
   Each accepted submission adds one parcel and that quantity to the unit total.
3. Empty, non-integer and out-of-range submissions display
   `Enter a whole number from 1 to 5` and leave both totals unchanged.
4. Successful submission displays `Parcel added` and clears the quantity field.
5. Both accumulated totals survive background/foreground, activity recreation,
   and process termination followed by relaunch without data reset.
6. Explicitly clearing app data returns both totals to zero.

Observe the installed UI to establish locators. Derive expected totals from
these rules and chosen inputs. An emulator run establishes behavior for the
recorded Android image; it establishes no iOS, radio or physical-device coverage.
