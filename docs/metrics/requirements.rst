Requirements
============

.. needpie:: Requirements
   :labels: done, open
   :legend:
   :filter-func: filters.reqs_filter


**Requirements not implemented**

.. needtable::
   :columns: id, title
   :style: table

   results = []

   for need in needs:
        if need["type"] != "req":
            continue

        if need["status"] == "open":
            results.append(need)
