CREATE DATABASE nomina;
USE nomina;

-- Tabla de empleados
CREATE TABLE empleados (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    curp VARCHAR(18) UNIQUE NOT NULL,
    rfc VARCHAR(13) UNIQUE NOT NULL,
    nss VARCHAR(11) UNIQUE NOT NULL,
    puesto VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    salario_base DECIMAL(10,2) NOT NULL
);

-- Tabla de nóminas (un recibo por cada periodo)
CREATE TABLE nominas (
    id_nomina INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    fecha_emision DATE NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    total_percepciones DECIMAL(10,2) DEFAULT 0,
    total_deducciones DECIMAL(10,2) DEFAULT 0,
    total_neto DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE
);

-- Tabla de percepciones (ingresos extra del empleado)
CREATE TABLE percepciones (
    id_percepcion INT AUTO_INCREMENT PRIMARY KEY,
    id_nomina INT NOT NULL,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_nomina) REFERENCES nominas(id_nomina) ON DELETE CASCADE
);

-- Tabla de deducciones (impuestos, retenciones, etc.)
CREATE TABLE deducciones (
    id_deduccion INT AUTO_INCREMENT PRIMARY KEY,
    id_nomina INT NOT NULL,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_nomina) REFERENCES nominas(id_nomina) ON DELETE CASCADE
);

CREATE TABLE incapacidades (
    id_incapacidad INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dias_incapacidad INT NOT NULL,
    tipo VARCHAR(20) NOT NULL, -- Ej: "Enfermedad", "Maternidad", etc.
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE
);
