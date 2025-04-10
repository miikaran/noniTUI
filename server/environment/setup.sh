#!/bin/bash

#####################################
# MAKE SURE POSTGRESQL IS INSTALLED #
#####################################

export POSTGRES_USER=$(whoami) # <= If you change this: You need to modify peer authentication settings from pg_hba.conf
export POSTGRES_PASSWORD="nonipassword"
export POSTGRES_DB="nonidb"

echo "Starting to set up NoniDB environment..."

sudo -i -u postgres bash <<EOF

echo "Creating user: $POSTGRES_USER"
psql -c "CREATE USER \"$POSTGRES_USER\" WITH PASSWORD '$POSTGRES_PASSWORD';"

echo "Creating database: $POSTGRES_DB"
psql -c "CREATE DATABASE \"$POSTGRES_DB\";"

echo "Granting privileges to user: $POSTGRES_USER on database: $POSTGRES_DB"
psql -c "GRANT ALL PRIVILEGES ON DATABASE \"$POSTGRES_DB\" TO \"$POSTGRES_USER\";"

EOF

sql_files=("tables.sql" "functions.sql" "triggers.sql")
postgres_sql_folder="/tmp"

for file in "${sql_files[@]}"
do
    if [[ -f "$file" ]]; then
        echo "Copying $file to $postgres_sql_folder"
        sudo cp $file $postgres_sql_folder
        sudo chown postgres:postgres $postgres_sql_folder/$file
        echo "Executing $file..."
        psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$postgres_sql_folder/$file"
    else
        echo "$file not found, stopping."
        break
    fi
done

echo "If no error messages on the screen, it maybe worked :)"