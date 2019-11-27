# -*- coding: utf-8 -*-

# shlib/mysql.sh
#
# Library functions for Bourne shell scripts: (Korp) MySQL database
# processing
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="msgs file"
. $_shlibdir/loadlibs.sh


# Functions

# run_mysql [--auth | --table table_name] [sql_command | ""]
#           [MySQL options ...]
#
# Run sql_command on the Korp database using MySQL and get the raw
# output (TSV format; first line containing column names).
#
# If --auth is specified, use the Korp authorization database instead
# of the main database. If --table is specified, use the authorization
# database if table_name begins with "auth_", otherwise the main
# database. Note that this assumes that only the authorization
# database has table names beginning "auth_" and that all the table
# names in the authorization database begin with it.
#
# If sql_command is omitted or empty, the SQL commands are read from
# stdin.
#
# MySQL username and password may be specified via the environment
# variables KORP_MYSQL_USER and KORP_MYSQL_PASSWORD. Additional MySQL
# options may be specified after sql_command. If additional MySQL
# options are specified and the input should be read from stdin,
# sql_command needs to be specified as an empty string.
run_mysql () {
    local _db sql_cmd
    _db=$korpdb
    if [ "x$mysql_bin" = x ]; then
	warn "MySQL client mysql not found"
	return 1
    fi
    if [ "x$1" = "x--auth" ]; then
	_db=$korpdb_auth
	shift
    elif [ "x$1" = "x--table" ]; then
	shift
	# Test if the table name begins with "auth_"
	if [ "$1" != "${1#auth_}" ]; then
	    _db=$korpdb_auth
	fi
	shift
    fi
    sql_cmd=$1
    # Unlike Bash, Dash gives an error message when trying to shift
    # past the end of the arguments, so test that there are arguments
    # left before shifting.
    if [ "$#" != 0 ]; then
	shift
    fi
    if [ "x$sql_cmd" = x ]; then
	sql_cmd=$(cat)
    fi
    # SET SQL_BIG_SELECTS=1 is needed for large SELECT (and other)
    # operations. Does it make the performance suffer for operations
    # not requiring it? If it does, we could have an option (--big?)
    # for using it.
    sql_cmd="SET SQL_BIG_SELECTS=1; $sql_cmd"
    $mysql_bin $mysql_opts --batch --raw --execute "$sql_cmd" "$@" $_db
}

# mysql_table_exists table_name
#
# Return true if table table_name exists in the Korp MySQL database.
# If table_name begins with "auth_", use the authorization database.
mysql_table_exists () {
    local table result
    table=$1
    result=$(run_mysql --table $table "DESCRIBE $table;" 2> /dev/null)
    if [ "x$result" = x ]; then
	return 1
    fi
}

# mysql_list_table_cols table_name
#
# List the column names of the Korp MySQL database table table_name
# (empty if the table does not exist). If table_name begins with
# "auth_", use the authorization database.
mysql_list_table_cols () {
    local table
    table=$1
    run_mysql --table $table "SHOW COLUMNS FROM $table;" 2> /dev/null |
    tail -n+2 |
    cut -d"$tab" -f1
}


# Initialize variables

# Korp MySQL database
korpdb=korp
# Korp MySQL database for authorization
korpdb_auth=korp_auth
# Unless specified via environment variables, assume that the Korp
# MySQL database user and password are specified in a MySQL option
# file
mysql_opts=
if [ "x$KORP_MYSQL_USER" != "x" ]; then
    mysql_opts="$mysql_opts --user=$KORP_MYSQL_USER"
elif [ "x$MYSQL_USER" != "x" ]; then
    mysql_opts="$mysql_opts --user=$MYSQL_USER"
fi
if [ "x$KORP_MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$KORP_MYSQL_PASSWORD"
elif [ "x$MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$MYSQL_PASSWORD"
fi
if [ "x$KORP_MYSQL_BIN" != "x" ]; then
    mysql_bin=$KORP_MYSQL_BIN
elif [ -x /opt/mariadb/bin/mysql ]; then
    # MariaDB on the Korp server
    mysql_bin="/opt/mariadb/bin/mysql --defaults-extra-file=/var/lib/mariadb/my.cnf"
else
    mysql_bin=$(find_prog mysql)
    if [ "x$(run_mysql ";" 2>&1)" != x ]; then
	mysql_bin=
    fi
fi
