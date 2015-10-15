CREATE TABLE channels
(segment_id		INTEGER		PRIMARY KEY,
 added			DATETIME	DEFAULT CURRENT_TIMESTAMP,
 absolute_uri		TEXT(1023)	UNIQUE NOT NULL,
 proto_options		TEXT(1023), -- space-separated --
 title			TEXT(1023),
 duration		REAL		DEFAULT NULL,
 program_date_time	DATETIME,
 key			TEXT(1023)
 );

CREATE TABLE channel_status
(segment_id			INTEGER		NOT NULL,
 uri_checked			DATETIME	DEFAULT CURRENT_TIMESTAMP,
 uri_status			INTEGER,
 thumbnail_directory		TEXT(1023),
 thumbnail_filenames		TEXT(1023), -- semicolon-separated --
 FOREIGN KEY(segment_id) REFERENCES channels(segment_id) ON UPDATE CASCADE ON DELETE CASCADE
 );

CREATE VIEW valid_channels AS
SELECT * FROM channels WHERE segment_id IN (SELECT segment_id FROM channel_status WHERE uri_status == 200);

