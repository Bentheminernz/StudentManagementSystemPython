from Utils.Database import Database
from Utils.ViewModels.ClassViewModel import ClassViewModel


def test_class_view_model_initialization():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    assert len(vm.classes) == 2
    assert vm.classes[0].name == "Math 101"
    assert vm.classes[1].name == "Science 101"
    db.close()


def test_get_class_by_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    cls = vm.get_class_by_id(1)
    assert cls is not None
    assert cls.name == "Math 101"
    db.close()


def test_get_class_by_id_boundary():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    cls = vm.get_class_by_id("invalid_id")
    assert cls is None
    db.close()


def test_add_class():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    vm.add_class("History 102", 2)
    classes = vm.classes
    assert len(classes) == 3
    assert classes[2].name == "History 102"
    db.close()


def test_delete_class():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    vm.delete_class(1)
    classes = vm.classes
    assert len(classes) == 1
    assert all(c.id != 1 for c in classes)
    db.close()


def test_update_class():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    vm.update_class(1, "Advanced Math 101", 2)
    classes = vm.classes
    assert len(classes) == 2
    updated_class = vm.get_class_by_id(1)
    assert updated_class.name == "Advanced Math 101"
    db.close()


# boundary/edge cases
def test_class_view_model_empty_db():
    db = Database(db_path=":memory:", seed_defaults=False)
    vm = ClassViewModel(db)
    assert vm.classes == []
    db.close()


def test_get_class_by_id_nonexistent():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    cls = vm.get_class_by_id(9999)
    assert cls is None
    db.close()


def test_get_class_by_id_invalid_type():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    cls = vm.get_class_by_id("not_an_int")
    assert cls is None
    db.close()


def test_add_multiple_classes_same_teacher():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    vm.add_class("Art 101", 1)
    vm.add_class("Music 101", 1)
    assert len(vm.classes) == 4
    assert any(c.name == "Art 101" for c in vm.classes)
    assert any(c.name == "Music 101" for c in vm.classes)
    db.close()


def test_delete_class_nonexistent_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    vm.delete_class(9999)
    assert len(vm.classes) == 2
    db.close()


def test_update_class_nonexistent_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    vm.update_class(9999, "Ghost Class", 1)
    assert len(vm.classes) == 2
    assert all(c.name != "Ghost Class" for c in vm.classes)
    db.close()


def test_delete_all_classes():
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = ClassViewModel(db)
    vm.delete_class(1)
    vm.delete_class(2)
    assert vm.classes == []
    db.close()
