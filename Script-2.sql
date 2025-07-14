drop table service;
drop table device;
drop table record;


CREATE TABLE service (
  id SERIAL PRIMARY KEY,
  name TEXT
);


CREATE TABLE device (
  id SERIAL PRIMARY KEY,
  service_id INT REFERENCES service(id)
);


CREATE TABLE record (
  id SERIAL PRIMARY KEY,
  device_id INT REFERENCES device(id),
  timestamp TIMESTAMP,
  value FLOAT,
  status TEXT default 'valido'
);



delete from service;
delete from device;
delete from record;


--Casos de prueba
INSERT INTO record (device_id, timestamp, value)
VALUES 
  (1, '2025-07-08 08:15:00', 300),
  (1, '2025-07-08 08:30:00', 410),
  (1, '2025-07-08 08:45:00', 520);

INSERT INTO record (device_id, timestamp, value)
VALUES 
  (1, '2025-07-08 10:15:00', 0),
  (1, '2025-07-08 10:30:00', 0),
  (1, '2025-07-08 10:45:00', 0);
  
select * from record where timestamp = '2025-07-08 08:45:00'

