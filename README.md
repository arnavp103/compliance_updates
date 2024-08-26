# UAE Financial Compliance Notification Service
When run as a service, notifies stakeholders of updates to regulations for entities in the financial sector of the UAE.

Currently polls from:

	- The Central Bank of the UAE's website.
	- The Ministry of the Economy's website


## Installation

### Pip Installation

Assuming you have pip installed, run the following command:

```bash

pip install -r requirements.txt

```

Then to run the service:

```bash

python main.py

```


### Poetry Installation

Assuming you have pipx installed, run the following command:

```bash

pipx install poetry # skip if you already have poetry installed

poetry install

```

Then to run the service:

```bash

python main.py

```

## How it Works

First everyday we fetch the relevant documents.
We then compare with a cache of yesterday's documents.

The file structure looks something like this:

```
documents/
├── new
│   ├── cbuae
│   │   └── Central Bank Provisions
│   │       ├── Circular No. 1:2023 on the Regulation of the Licensing of Payment Service Providers.pdf
│	│	    └── etc ...
│   └── moec
│       ├── Anti-Money Laundering Crimes Legislations
│       │   ├── Cabinet Decision No (109) of 2023 on regulating the procedures of the beneficial owner prodcedures.pdf
│       │   ├── Cabinet Decision No (10) of 2019 concerning the Executive Regulations of Federal Decree Law No (20) of
│       │   │── Federal Law No (2) of 2014 on Small and Medium Projects and Enterprises.pdf
│		│	└── etc ...
│       └── Trading by Modern Technological Means
│           └── Federal Decree-Law No. 14:2023 on Trading by Modern Technological Means.pdf
└── prev
    ├── cbuae
    │   └── Anti-Money Laundering Crimes Legislations
    │
    └── moec

```

With repeated folders and files for the most part in new and prev.

Then we have to compare the pdfs to find the difference.

We can't just feed the two pdfs into an LLM and ask for the differences.

Consider an average of 250 words per page.
Then with an LLM with a context of 100,000 tokens giving it 100 pages will fill 33% of the context by itself.

(250 * 100 * 1.333) / 100000 ~ 0.33

Since these documents are ~800 pages each and we need 2 copies for the differences this can't work.
Not to mention it's overly expensive.


Once we have the difference we have to use an email service like postmark to send the emails.