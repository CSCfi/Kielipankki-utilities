FIN-CLARIN Relation Tools (rel tools)
=====================================
_version 0.1.1 (2020-05-03)_

Rel tools are command-line tools for the investigation and
manipulation of relations in the form of files that contain
Tab-Separated Values (TSV) in named fields:

  * unique field names
  * unique rows
  * order does not matter

Order, whether of fields or rows, is maintained for convenience.
Fields are identified by name and records by content.

The tools are implemented in Python (version 3.5 or newer) in
GNU/Linux environments, using `sort(1)` much and `cat(1)`, `head(1)`,
and `tail(1)` some.

Terminology
-----------

A **relation** is a set of **records** of the same **type**. A type
consists of field names. The **values** in the **fields** are
character strings.  Elsewhere, a record might be called a "tuple" and
a field, or a field name, might be called an "attribute". Being a
**set** means that any record (of the given type) either is or is not
in the relation: there is no uncertainty, or degree, or multiplicity,
of membership, and no specified position.

A written presentation of a relation has a **head** that consists of
the field names in some order, followed by a **body** that consists of
the records in some order, the number and order of the fields in each
record matching the head. These are the rows, or lines, in the TSV
file.

Initial rel tools
-----------------

  * `rel-cmp` compares two relations (since version 0.1.1)

  * `rel-from` collects records into a relation

  * `rel-rename` is much under-appreciated

  * `rel-head` extracts a convenient sample
  * `rel-tail` extracts a convenient sample
  * `rel-sample` extracts a random sample

  * `rel-keep` projects to named fields
  * `rel-keepc` projects with count
  * `rel-drop` projects to other fields
  * `rel-dropc` projects with count

  * `rel-sum` is tagged disjoint union
  * `rel-union` is union
  * `rel-meet` is intersection
  * `rel-sans` is difference
  * `rel-symm` is symmetric difference (maybe?)

  * `rel-join` is (natural) join
  * `rel-match` matches _some_ record
  * `rel-miss` matches _no_ record
  * `rel-image` drops the match of a match
  * `rel-compose2` drops the match of a join

(Incidentally, the names of `rel-join` and `rel-meet` are false
friends: the "join" and "meet" of a Boolean lattice are `rel-union`
and `rel-meet`, whereas `rel-join` actually is the same as `rel-meet`
when the relations are of the same type. Also, the name of `rel-head`
has nothing to do with the division of a relation file into a "head"
and a "body".)

Eventual rel tools
------------------

The most important missing tools are likely to be entire families,
possibly containing mini-languages of expressions that can refer to
the values in the records by the field name. Some of these uses are
straightforward (some are already available in the original
incarnation of these tools in Mylly).

These important missing multi-tools would be these two:

  * `rel-extend` extends each record functionally
  * `~rel-select~` `rel-filter` selects records conditionally

Useful tools like `rel-keepc`, which describes each _group_ of
records, are quite probably missing and can be easily added once
identified.

And a couple of more minor missing tools seem practically desirable in
some form, maybe:

  * `rel-test` would test some property of a relation
  * `rel-info` would describe a relation somehow

The input from the surrounding world is envisioned to come from text
corpora, especially structured and annotated corpora in the VRT form
that FIN-CLARIN prepares and maintains for the Language Bank.
Relations could then be used to feed back on said annotations, or
passed on to any environment where tabular data is understood and can
be further manipulated for greater insight and more advanced
entertainment.

Acknowledgment
--------------

These rel tools implement relation algebra as advocated for database
systems by Chris Date and Hugh Darwen, presumably originating with Ted
Codd. The value types of rel tools are quite impoverished, being all
strings, but the relations themselves are quite seriously sets of
records with named fields.
