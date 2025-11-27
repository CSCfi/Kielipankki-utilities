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
    if [ "x$mysql_error" != x ]; then
	warn "$mysql_error"
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

# run_mysqldump [mysqldump options] table ...
#
# Run mysqldump, dumping the listed tables in Korp database, with
# possible mysqldump options.
run_mysqldump () {
    local extra_opts
    extra_opts=
    if [ "x$mysqldump_error" != x ]; then
        warn "$mysqldump_error"
        return 1
    fi
    while true; do
        case "$1" in
            -* )
                extra_opts="$extra_opts $1"
                shift
                ;;
            * )
                break
                ;;
        esac
    done
    $mysqldump_bin --no-autocommit $mysql_opts $extra_opts $korpdb "$@" 2> /dev/null
}

# mysql_table_exists table_name
#
# Return true if table table_name exists in the Korp MySQL database.
# If table_name begins with "auth_", use the authorization database.
mysql_table_exists () {
    local table result
    table=$1
    result=$(run_mysql --table $table "DESCRIBE \`$table\`;" 2> /dev/null)
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
    run_mysql --table $table "SHOW COLUMNS FROM \`$table\`;" 2> /dev/null |
    tail -n+2 |
    cut -d"$tab" -f1
}


# mysql_get_database_charset [--auth | --table table_name]
#
# Get the default character set for the Korp database (or the
# authorization database if --auth is specified or if table_name
# begins with "auth_").
mysql_get_database_charset () {
    run_mysql "$@" "SELECT @@character_set_database;" |
        tail -n1
}


# Initialize variables

# Korp MySQL database
korpdb=korp
# Korp MySQL database for authorization
korpdb_auth=korp_auth
# Unless specified via environment variables, assume that the Korp
# MySQL database host, user and password are specified in a MySQL
# option file
mysql_opts=
if [ "x$KORP_MYSQL_HOST" != "x" ]; then
    mysql_opts="$mysql_opts --host=$KORP_MYSQL_HOST"
elif [ "x$MYSQL_HOST" != "x" ]; then
    mysql_opts="$mysql_opts --host=$MYSQL_HOST"
fi
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
# If the mysql binary or the Korp MySQL database cannot be accessed,
# $mysql_error contains an error message (otherwise empty) and
# $mysql_bin is empty
mysql_error=
if [ "x$KORP_MYSQL_BIN" != "x" ] && [ -x "$KORP_MYSQL_BIN" ]; then
    mysql_bin=$KORP_MYSQL_BIN
elif [ -x /opt/mariadb/bin/mysql ]; then
    # MariaDB on the Korp server
    mysql_bin="/opt/mariadb/bin/mysql --defaults-extra-file=/var/lib/mariadb/my.cnf"
else
    mysql_bin=$(find_prog mysql)
    if [ $? != 0 ]; then
	mysql_error="MySQL client mysql not found"
        mysql_bin=
    fi
fi
mysql_error="$(run_mysql ";" 2>&1)"
if [ "x$mysql_error" != x ]; then
    mysql_error="Cannot access Korp MySQL database: $mysql_error"
    mysql_bin=
fi

# Find the mysqldump binary
if [ "x$KORP_MYSQLDUMP_BIN" != "x" ] && [ -x "$KORP_MYSQLDUMP_BIN" ]; then
    mysqldump_bin=$KORP_MYSQLDUMP_BIN
elif [ -x /opt/mariadb/bin/mysqldump ]; then
    # MariaDB on the Korp server; is this still needed?
    mysqldump_bin="/opt/mariadb/bin/mysqldump --defaults-extra-file=/var/lib/mariadb/my.cnf"
else
    mysqldump_bin=$(find_prog mysqldump)
    if [ $? != 0 ]; then
	mysqldump_error="mysqldump not found"
        mysqldump_bin=
    fi
fi
