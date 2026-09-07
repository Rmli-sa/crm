This module reuses the CRM lead model to manage leads and opportunities
coming from suppliers. The flow mirrors the CRM one: a lead gets a *request
type* (customer or supplier), and supplier opportunities are converted into
requests for quotation and purchase orders instead of quotations and sales
orders.

The two apps split the same records:

- **SRM** only shows supplier leads and opportunities.
- **CRM** shows everything else, including records whose request type was
  never set (imports, incoming e-mails, website forms, other integrations).
  Such records stay visible and can be moved to either app by editing the
  request type on the lead form.

Supplier opportunities carry *RFQs* and *Purchase Orders* smart buttons that
open the linked purchase documents, and a purchase order can be linked back
to its supplier opportunity.
