import collections
from sqlalchemy import orm, and_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import functools
from multitenantcrud.paginate import paginate


def flush(func):
    @functools.wraps(func)
    def wrapper(session, *args, **kwargs):
        ret = func(session, *args, **kwargs)
        session.flush()
        return ret

    return wrapper


@flush
def create(session, company, entity_class, **kwargs):
    entity = entity_class(**kwargs)

    if _has_company_field(entity):
        entity.company = company

    session.add(entity)
    return entity


def read(session, company, entity_class, id=None, **kwargs):
    assert id is not None or kwargs

    query = _get_query(session, company, entity_class)
    if id is not None:
        if isinstance(id, list):
            entities = query.filter(entity_class.id.in_(id)).all()

            return [a for a in entities if
                    _get_company(a, company) == company]
        else:
            entity = query.enable_assertions(False).get(id)
            if _get_company(entity, company) == company:
                return entity

    query = query.filter_by(**kwargs)
    try:
        entity = query.enable_assertions(False).one()

        if _get_company(entity, company) == company:
            return entity

    except MultipleResultsFound:
        return None
    except NoResultFound:
        return None


@flush
def update(session, company, entity_class, id, **kwargs):
    entity = read(session, company, entity_class, id=id, **kwargs)

    for key, value in kwargs.iteritems():
        setattr(entity, key, value)

    return entity


@flush
def update_entity(session, company, entity):
    return entity


@flush
def delete(session, company, entity_class, id):
    entity = read(session, company, entity_class, id=id)

    session.delete(entity)


def object_query(session, company, entity_class, **kwargs):
    kwargs.pop('_page', None)
    kwargs.pop('_page_size', None)
    return _get_query(session, company, entity_class, **kwargs)


def object_list(session, company, entity_class, **kwargs):
    page = kwargs.pop('_page', None)
    page_size = kwargs.pop('_page_size', 20)
    query = object_query(session, company, entity_class, **kwargs)

    if page is not None:
        return paginate(query, page, page_size)
    return query.all()


def object_count(session, company, entity_class, **kwargs):
    kwargs.pop('_page', None)
    kwargs.pop('_page_size', None)
    return _get_query(session, company, entity_class, **kwargs).count()


def create_or_update(session, company, entity_class, **kwargs):
    entity = read(session, company, entity_class, **kwargs)

    if entity:
        kwargs.pop('id', None)
        update(session, company, entity_class, id=entity.id, **kwargs)
    else:
        entity = create(session, company, entity_class, **kwargs)
    session.flush()

    return entity


def _get_query(session, company, entity_class, **kwargs):
    OPTIONS = {

    }

    query = session.query(entity_class)

    if _has_company_field(entity_class):
        query = query.filter_by(company=company)


    if kwargs:
        conditions = []
        for attribute, value in kwargs.iteritems():
            condition = None
            if isinstance(value, list):
                if value:
                    condition = getattr(entity_class, attribute).in_(value)
            else:
                condition = getattr(entity_class, attribute) == value

            if condition is not None:
                conditions.append(condition)

        query = query.filter(and_(*conditions))

    return query.options(*OPTIONS.get(entity_class, []))

def _has_company_field(entity):
    mapper = entity.__mapper__
    return mapper.has_property('company')

def _get_company(entity, default):
    if entity and _has_company_field(entity):
        return entity.company
    return default
