# LinkCheckerOclc

The following code queries OCLC's Knowledge Base API for a particular collection (using the collection ID) and sends a report (Kbart as attachment) by email of all the redirecting and broken links.
This code has been designed to check Open Access collections.

It is meant to be programmed to run once a month.

Instructions to use the code:

There are 3 preliminary steps:
1.	You must download python on the computer you are using.

2.	You must request an API wskey from OCLC. I used the online platform: https://platform.worldcat.org/wskey/wayf 

3.	I automated the code to run once a month and send me an email with the broken links. You need to enter the email that is sending      (and the password of that email). I created an empty gmail, that I only use for this, mostly or security reasons. You also need to      let less secure apps access your account, when using gmail:https://support.google.com/accounts/answer/6010255 


Then you need to change a few things in the code, without removing any quotation marks:
1.	At line 26 and 48: you need to replace “ThisIsMyWsApiKey” with your key. Leave the “wskey=” before your key.

2.	At line 147: replace “myPassword” with the password of your sender email.

3.	At line 160: replace "ThisIsMyCollectionID" with the collection ID of the collections you want to test. Putting more than one collection can take a long time, depending on the amount of titles in the collection.

4.	At line 179 and 183: replace: fromEmail@gmail.com with the sender email, toEmail@email.ca with the receiver email, "openAccess_redirects_results.csv" with the filename, if you want a different one, and "Report of redirecting links in collection " + collection+ ". The links have been corrected in the attached file." With the message you want in the email.

You need to install python libraries (requests.)

Finally you run the code.
