drop database simulador;
create database simulador;
use simulador;

create table simu(
	idsim int,
    mem_size int not null,
    so_porcent int not null,
    fecha date,
    primary key (idsim)
    );

create table procesos(
	idpc int AUTO_INCREMENT,
    descripcion varchar(30),
    priori int,
    pc_size int not null,
    ti int,
    ta int not null,
    primary key (idpc)
    );

create table rafagas(
	idraf int,
    idpc int,
    raf_type char(3) not null,
    ti int not null,
    primary key (idpc,idraf),
    foreign key (idpc) references procesos (idpc)
    on delete cascade on update cascade
    );

create table part_fija(
	idsim int not null,
    idpart int,
    dir_rli int not null,
    estado char(1) not null,
    frag_int int,
    part_size int not null,
    primary key (idsim,idpart),
    foreign key (idsim) references simu (idsim)
    on delete cascade on update cascade
    );

create table part_var(
	idsim int not null,
	idpart int,
    dir_rli int not null,
    part_size int not null,
    idpc int not null,
    primary key (idsim,idpc,idpart),
    foreign key (idpc) references procesos (idpc)
    on delete cascade on update cascade,
    foreign key (idsim) references simu (idsim)
    on delete cascade on update cascade
    );
    
create table ocupa(
	idpc int not null,
    idpart int not null,
	idsim int not null,
    primary key (idpc, idsim, idpart),
    foreign key  (idpc) references procesos (idpc)
    on delete no action on update no action,
    foreign key (idsim, idpart) references part_fija (idsim, idpart)
    on delete no action on update no action
    );

    