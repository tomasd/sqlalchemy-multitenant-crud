import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as orm
import multitenantcrud as crud
from nose.tools import eq_

Model = declarative_base()
Session = orm.sessionmaker()
session = orm.scoped_session(Session)

class Company(Model):
    __tablename__ = 'company'
    id = sa.Column(sa.Integer, primary_key=True)


class MyModel(Model):
    __tablename__ = 'my_model'
    id = sa.Column(sa.Integer, primary_key=True)
    company_id = sa.Column(None, sa.ForeignKey('company.id'))
    company = orm.relation('Company')
    name = sa.Column(sa.String(255))


def setUp():
    engine = sa.create_engine('sqlite://')
    session.bind = engine
    Model.bing = engine
    Model.metadata.create_all(bind=engine)


def test_crud():
    company = Company()
    session.add(company)

    assert [] == crud.object_list(session, company, MyModel)

    obj = crud.create(session, company, MyModel, name='xxx')
    assert obj.name == 'xxx'
    session.commit()

    read_obj = crud.read(session, company, MyModel, obj.id)
    assert read_obj == obj
    assert 1 == crud.object_count(session, company, MyModel)
    assert [read_obj] == crud.object_list(session, company, MyModel)

    crud.update(session, company, MyModel, obj.id, name='aaa')
    session.commit()

    update_obj = crud.read(session, company, MyModel, obj.id)
    assert update_obj.name == 'aaa'

    crud.delete(session, company, MyModel, obj.id)
    delete_obj = crud.read(session, company, MyModel, obj.id)
    assert delete_obj is None

    assert 0 == crud.object_count(session, company, MyModel)


def test_multi_param_query():
    company = Company()
    session.add(company)

    obj1 = crud.create(session, company, MyModel, name='obj1')
    obj2 = crud.create(session, company, MyModel, name='obj2')

    eq_({obj1, obj2},
        set(crud.object_list(session, company, MyModel, name=['obj1', 'obj2'])))
