# LC-cutter

Every month, the Library of Congress releases changes and additions to LC classifications published to classweb.org/approved/. Most recently, the Library of Congress has begun releasing changed classification patterns for racial and ethnic group terms in response to pressure from the cataloging community to be more inclusive. NCSU Libraries has an interest in tracking and implementing these changes locally. I explored how to process these monthly lists using Python to filter the monthly results into a spreadsheet of changed classifications that could be reviewed and implemented as appropriate.

This script looks at the webpage to filter out results based on the words “see” and “CANCEL" and exports these into a spreadsheet to the user's desktop. It requires the following libraries to run:

- pandas

This script is currently a work-in-progress. The first tab, detailing cancelled/updated classification numbers and their captions, seems to work based on testing so far. The remaining tabs have incomplete information.
