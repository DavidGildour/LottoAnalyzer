import analyzer.db_manager as db_manager


def get_results_by_numbers(numbers: str):
    delimiter = "," if "," in numbers else " "
    numbers = numbers.split(delimiter)
    if all([num.strip().isdigit() for num in numbers]):
        numbers = list(map(lambda s: "{:02}".format(int(s)), numbers))
        return db_manager.get_records_by_numbers(numbers)
    else:
        return []
