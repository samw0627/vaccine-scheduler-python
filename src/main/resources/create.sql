CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patient (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
    Appointmet_ID int IDENTITY(1,1) PRIMARY KEY,
    Patient_Username varchar(255) REFERENCES Patient,
    Caregiver_Username varchar(255) REFERENCES Caregivers,
    Time date,
    Vaccine_Name varchar(255) REFERENCES Vaccines,
)