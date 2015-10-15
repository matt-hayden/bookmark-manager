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
(segment_id	INTEGER		NOT NULL,
 checked_on	DATETIME	DEFAULT CURRENT_TIMESTAMP,
 status		INTEGER,
 FOREIGN KEY(segment_id) REFERENCES channels(segment_id) ON UPDATE CASCADE ON DELETE CASCADE
 );

CREATE TABLE channel_thumbnails
(segment_id			INTEGER		NOT NULL,
 created			DATETIME	DEFAULT CURRENT_TIMESTAMP,
 thumbnail_directory		TEXT(1023),
 thumbnail_filenames		TEXT(1023), -- semicolon-separated --
 FOREIGN KEY(segment_id) REFERENCES channels(segment_id) ON UPDATE CASCADE ON DELETE CASCADE
 );

CREATE TABLE channel_captures
(segment_id			INTEGER		NOT NULL,
 created			DATETIME	DEFAULT CURRENT_TIMESTAMP,
 capture_directory		TEXT(1023),
 capture_filenames		TEXT(1023), -- semicolon-separated --
 converted			INTEGER		DEFAULT 0,
 FOREIGN KEY(segment_id) REFERENCES channels(segment_id) ON UPDATE CASCADE ON DELETE CASCADE
 );

CREATE VIEW status_age AS
SELECT *, (date('now')-checked_on) AS age FROM channel_status;

CREATE VIEW thumbnails_age AS
SELECT *, (date('now')-created) AS age FROM channel_thumbnails;

CREATE VIEW captures_age AS
SELECT *, (date('now')-created) AS age FROM channel_captures;

CREATE VIEW latest_status AS
SELECT segment_id, FIRST(checked_on), FIRST(status), FIRST(age) FROM status_age
GROUP BY segment_id ORDER BY age;

CREATE VIEW valid_channels AS
SELECT * FROM channels AS C JOIN channel_status AS S ON C.segment_id=S.segment_id WHERE S.status == 200;

CREATE VIEW latest_thumbnails AS
SELECT * FROM thumbnails_age AS T
JOIN valid_channels as C ON C.segment_id=T.segment_id
ORDER BY age;

CREATE VIEW recent_captures AS
SELECT * FROM captures_age
GROUP BY segment_id ORDER BY age;
