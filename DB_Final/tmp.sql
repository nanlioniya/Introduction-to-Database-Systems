CREATE TABLE parking_location (
	PARKNO int,
	PARKINGNAME varchar(50),
	ADDRESS varchar(50),
	X numeric(10, 7),
	Y numeric(10, 7),
	primary key(PARKNO)
);

CREATE TABLE parking_info (
	PARKNO int,
	BUSINESSHOURS_start int,
	BUSINESSHOURS_end int,
	WEEKDAYS varchar(50),
	HOLIDAY varchar(50),
	FREESPACECAR int,
	TOTALSPACECAR int, 
	FREESPACEMOT int, 
	TOTALSPACEMOT int,
	primary key(PARKNO)
);