#! /bin/sh

# Reindex Korp MySQL tables for word picture with covering indexes
#
# FIXME: If one of the ALTER TABLE specifications fails, the whole
# statement fails.


alter_specs="@ rel head_rel dep_rel strings"

alter_='
  DROP PRIMARY KEY,
  DROP KEY `head`,
  DROP KEY `dep`,
  DROP KEY `bfhead`,
  DROP KEY `bfdep`,
  DROP KEY `wfhead`,
  DROP KEY `wfdep`,
  ADD PRIMARY KEY (`head`,`wfhead`,`dep`,`rel`,`freq`,`id`),
  ADD KEY `dep-wfdep-head-rel-freq-id` (`dep`,`wfdep`,`head`,`rel`,`freq`,`id`),
  ADD KEY `head-dep-bfhead-bfdep-rel-freq-id` (`head`,`dep`,`bfhead`,`bfdep`,`rel`,`freq`,`id`),
  ADD KEY `dep-head-bfhead-bfdep-rel-freq-id` (`dep`,`head`,`bfhead`,`bfdep`,`rel`,`freq`,`id`)'
alter_rel='
  DROP KEY `rel`,
  ADD PRIMARY KEY (`rel`,`freq`)'
alter_head_rel='
  DROP KEY `head`,
  DROP KEY `rel`,
  ADD PRIMARY KEY (`head`,`rel`,`freq`)'
alter_dep_rel='
  DROP KEY `dep`,
  DROP KEY `rel`,
  ADD PRIMARY KEY (`dep`,`rel`,`freq`)'
alter_strings='
  DROP PRIMARY KEY,
  DROP KEY `string`,
  ADD PRIMARY KEY (`string`,`id`,`pos`,`stringextra`),
  ADD KEY `id-string-pos-stringextra` (`id`,`string`,`pos`,`stringextra`)'

change_indexes () {
    corp=$1
    corp_u=$(echo $corp | sed -e 's/.*/\U&\E/')
    echo "Reindexing $corp"
    for alter_spec in $alter_specs; do
	alter_spec=$(echo _$alter_spec | sed -e 's/_@//')
	printf "  relations_$corp_u$alter_spec"
	{
	    echo 'ALTER TABLE `relations_CORPUS`'
	    eval echo "\$alter_$alter_spec"
	    echo ';'
	} |
	sed -e "s/CORPUS/$corp_u/g" |
	/usr/bin/time -f "\t%E %U %S" mysql --batch --force korp
    done
}

for corpus in "$@"; do
    change_indexes $corpus
done
