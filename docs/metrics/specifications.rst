Specifications
==============

.. needpie:: Specifications
   :labels: done, open
   :legend:
   :filter-func: filters.spec_filter

**Specifications not implemented**

.. needtable::
   :columns: id, title
   :style: table

   results = []

   for need in needs:
        if need["type"] != "spec":
            continue

        if need["status"] == "open":
            results.append(need)