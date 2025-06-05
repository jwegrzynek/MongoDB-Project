# 🔧 Jak uruchomić bazę danych

### ✨ Klonowanie

```bash
git clone https://github.com/jwegrzynek/MongoDB-Project.git
```

### ✨ Konfiguracja środowiska
```bash
cd MongoDB-Project
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

### ✨ Tworzenie bazy danych
```bash
python create_database.py

```

# 📖 Opis bazy danych

Baza danych zawiera informacje o uratowanych zwierzętach oraz informacje związane z ich adopcją.

## 🎯 Pola główne

| Pole              | Typ danych        | Wymagane | Opis                                                 |
| ----------------- | ----------------- | -------- | ---------------------------------------------------- |
| `name`            | `string` / `null` | ✅        | Imię zwierzęcia (jeśli dostępne)                     |
| `type`            | `string`          | ✅        | Typ zwierzęcia, np. `Dog`, `Cat`                     |
| `age`             | `int ≥ 0`         | ✅        | Wiek zwierzęcia w latach                             |
| `breed.primary`   | `string` / `null` | ✅        | Główna rasa                                          |
| `breed.secondary` | `string` / `null` | ✅        | Drugorzędna rasa (jeśli dotyczy)                     |
| `gender`          | `string`          | ✅        | `Male`, `Female`, `Mixed`, `Unknown`                 |
| `colors`          | `array[string]`   | ✅        | Lista kolorów sierści                                |
| `maturitySize`    | `string`          | ✅        | `Small`, `Medium`, `Large`, `Extra Large`, `Unknown` |
| `furLength`       | `string`          | ✅        | `Short`, `Medium`, `Long`, `Bald`, `Unknown`         |
| `medical`         | `object`          | ✅        | Informacje medyczne (szczegóły poniżej)              |
| `quantity`        | `int ≥ 1`         | ✅        | Liczba zwierząt w zgłoszeniu                         |
| `fee`             | `int ≥ 0`         | ✅        | Opłata adopcyjna                                     |
| `location`        | `string`          | ✅        | Miasto lub lokalizacja zwierzęcia                    |
| `rescuerId`       | `string`          | ✅        | Identyfikator osoby lub organizacji ratującej        |
| `rescueDate`      | `date`            | ✅        | Data uratowania zwierzęcia                           |
| `description`     | `string` / `null` | ✅        | Opis zwierzęcia (jeśli dostępny)                     |
| `adoption`        | `object`          | ✅        | Informacje adopcji (szczegóły poniżej)               |

## 🏥 Informacje medyczne (`medical`)

| Pole         | Typ    | Wartości dozwolone                                     | Wymagane | Opis                |
| ------------ | ------ | ------------------------------------------------------ | -------- | ------------------- |
| `vaccinated` | `string` | `Yes`, `No`, `Not sure`, `Unknown`                     | ✅        | Status szczepienia  |
| `dewormed`   | `string` | `Yes`, `No`, `Not sure`, `Unknown`                     | ✅        | Odrobaczenie        |
| `sterilized` | `string` | `Yes`, `No`, `Not sure`, `Unknown`                     | ✅        | Sterylizacja        |
| `health`     | `string` | `Healthy`, `Minor Injury`, `Serious Injury`, `Unknown` | ✅        | Ogólny stan zdrowia |



## 🏡 Informacje o adopcji (`adoption`)

| Pole             | Typ             | Wymagane | Opis                                                                                |
| ---------------- | --------------- | -------- | ----------------------------------------------------------------------------------- |
| `adopted`        | `bool`          | ✅        | Czy zwierzę zostało adoptowane                                                        |
| `adoptionDate`   | `date` / `null` | ❌        | Data adopcji (jeśli dotyczy)                                                          |
| `adoptionPeriod` | `string` / `null` | ❌        | Czas do adopcji: `Same Day`, `1-7 Days`, `8-30 Days`, `31-90 Days`, `Over 100 Days` |
| `daysInShelter`  | `int` / `null`  | ❌        | Liczba dni spędzonych w schronisku                                                    |
