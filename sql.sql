CREATE TABLE users (
	user_id					BIGINT		NOT NULL	PRIMARY KEY,
	username				VARCHAR(50)	NOT NULL,
	entry_date				TIMESTAMP	NOT NULL,
	is_bot_on				BOOLEAN		NOT NULL,

	is_subscription_active	BOOLEAN		NOT NULL,
	subscription_id			SMALLINT,
	subscription_begin_date	TIMESTAMP,

	is_test_active			BOOLEAN		NOT NULL,
	test_begin_date			TIMESTAMP,
	language				VARCHAR(2)	NOT NULL,
	chat_type				VARCHAR(10)
);

CREATE TABLE users_parametres (
	user_id			BIGINT		NOT NULL	PRIMARY KEY,
	limits			INTEGER,
	banks			TEXT		NOT NULL,
	markets			TEXT		NOT NULL,
	spread			REAL		NOT NULL,
	bid_type		VARCHAR(5)	NOT NULL,
	ask_type		VARCHAR(5)	NOT NULL,
	currencies		TEXT		NOT NULL,
	fiat			VARCHAR(5)	NOT NULL,
	signals_type	VARCHAR(8)	NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


CREATE TABLE available_markets (
	title	TEXT	NOT NULL	UNIQUE,
	p2p		BOOLEAN	NOT NULL,
	spot	BOOLEAN	NOT NULL
);
CREATE TABLE available_currencies (
	title	TEXT	NOT NULL	UNIQUE,
	p2p		BOOLEAN	NOT NULL,
	spot	BOOLEAN	NOT NULL
);
-- Import data from supported_banks.csv
/*
COPY supported_banks(fiat, bank, supported_markets, fiat_symbol)
FROM '%PATH%\supported_banks.csv'
DELIMITER ','
CSV HEADER;
*/
CREATE TABLE supported_banks (
	fiat				VARCHAR(50)	NOT NULL,
	bank				VARCHAR(30)	NOT NULL,
	supported_markets	TEXT		NOT NULL,
	fiat_symbol			VARCHAR(7)	NOT NULL
);

CREATE TABLE admins (
	admin_id	INTEGER			PRIMARY KEY,
	username	VARCHAR(255)	NOT NULL
);
CREATE TABLE chats (
	chat_id		BIGINT			PRIMARY KEY,
	admin_id	INT,
	FOREIGN KEY (admin_id) REFERENCES admins(admin_id),
	FOREIGN KEY (chat_id) REFERENCES users(user_id) ON DELETE CASCADE
);
