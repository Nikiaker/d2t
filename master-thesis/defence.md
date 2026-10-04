# Limit czasu

15 minutes

## Czas poświęcony na poszczególne części

- Wyjaśnienie czym jest D2T, metody, problemy, motywacja, interpretowalne metody, podział na 3 części: 3 minuty
- Meaning representation, zamysł metody 1, opis pipeline, omówienie wyników i wniosków: 6 minut
- Surface realization, przedstawienie AlphaEvolve, wyjaśnienie algorytmu, podanie setupów i omówienie wyników i wniosków: 6 minut
- Podsumowujące kontrybucje pracy: 1 minuta

## Szczegółowy tekst na slajdach

## PART 0

### Slajd 1

Dzień dobry, nazywam się Dominik Maćkowiak i mam przyjemność zaprezentować dokonania w mojej pracy magisterskiej, której tytuł po polsku to Intepretowalne metody konwersji danych do tekstu. Promotorem mojej pracy jest Pan Doktor Mateusz Lango.

### Slajd 2

Moja praca dotyczy tytułowego problemu data-to-text, który polega na przekształceniu surowych ustrukturyzowanych danych (takich jak tabele, pliki JSON, czy grafy) na tekst naturalny. Przykładem takiej konwersji może być przekształcenie grafu prognozy pogody na opis pogody w danym dniu.

### Slajd 3

Problem nie jest nowy, dlatego na przestrzeni lat powstały różne metody. Najstarszą metodą jest system rule-based, który polegaja na ręcznym stworzeniu szablonów, które pozwalają na uzupełnienie odpowiednich słów/zdań zależnie od daynch wejściowych. Innymi metodami, są metody statystczne i neuronowe, które znacząco zmniejszają nakład manualnego projektowania, ale wymagają zaprojektowania odpowiedniego modelu statystycznego. Innymi, najnowszymi podejściami, które są state-of-the-art to podejścia wykorzystujące architekturę transformers i pre-trenowane modele, które mogą być fine-tunowane dla konkretnego problemu lub nawet mając odpdowiednim prompt z instrukcją też można uzyskać satysfakcjonujący wynik.

### Slajd 4

Jednakże te metody mają swoje problemy. Systemy rule-based są łatwe w analizie i pozwalają na kontrolę tego, które fakty mają się znaleźć w finalnym tekście, ale wymagają ręcznego tworzenia szablonu co jest czasołchonne. Zaś systemy neuronowe i modele językowe zmniejszają nakład pracy i poprawiają płynność tekstu, ale są podatne na halucynacje, a więc mogą się pojawić w tekście informacje, których nie było w danych źródłowych lub któreś fakty mogą zostać pominięte. Do tego stworzenie takiego tekstu wymaga odpowiedniej selekcji danych źródłowych, agregacji, itd. i powód takich decyzji jest trudniejszy do intepretacji w przypadku modelów neuronowych.

### Slajd 5

Klasycznie w problemie data-to-text pomiędzy danymi a tekstem znajduje się wiele kroków pośrednich, które mają ułatawić zarządzanie systemami i generatorami. W tej pracy wyróżniłem jeden krok pośredni, którym jest Meaning Representation. Zamysłem tego kroku jest otrzymanie reprezentacji, która jest strukturą maszynową, a więc można ją łatwo poddać kolejnym procesom, oraz jest jednocześnie czytelna przez człowieka. Następnie mając tą reprezentację, możemy przekształcić ją na tekst naturalny. Proces ten nazywa się Surface realization.

### Slajd 6

Jako Meaning representation zostały wybrane trójki semantyczne, rozumiane jako uproszceznie trójek RDF. Ich zaletą jest to, że można zamodelować pewne relacje i fakty, bez narzucania konkretnej struktury gramatycznej. To sprawia, że z tych trójek mogą powstać różne naturalne teksty o tym samym znaczeniu.

### Slajd 7

Jak chodzi o sam Surface realization to istnieje praca stworzona przez Lango i innych, która przedstawia system agentów, których zadaniem jest stworzenie programu w języku Python na podstawie zadanego grafu wiedzy. Ten program przy podaniu na wejściu trójek semantycznych, przekształca je na tekst naturalny. Dzięki temu uzyskujemy w pełni intepretowalny Surface relization w postaci kodu w pythonie.

### Slajd 8

Aczkolwiek to podejście ma swoje wady: po pierwsze system zakłada, że Meaning representation już istnieje, a więc system go nie tworzy. Kolejna sprawą jest to, że agenci pracują indywidualnie nad poszczególnymi komponentami i nie znają całego kontekstu problemu, który rozwiązują. Do tego rozwiązanie może wpaść w lokalne minimum.

### Slajd 9

Tak więc ta praca magisterska proponuje dwie rzeczy: pierwsza to metody, które konstruują Meaning representation z surowych danych. Te metody, które przedstawię w dalszej części prezentacji, wykorzystują modele językowe do konstrukcji, więc metoda sama w sobie nie jest interpretowalna, aczkolwiek wynik już jest, co pozwala na ewaluację stworzonej reprezentacji z danymi źródłowymi.

### Slajd 10

Druga to usprawnienie Surface realization, poprzez użycie algorytmu ewolucyjnego, którego wynikem będzie w pełni intepretowalny program w Pythonie. Algorytmy ewolucyjne same w sobie są silne i pozwalają na szerszą eksplorację przestrzeni rozwiązań i łatwiejsze wyjście z lokalnego minimum.

Dalsza część prezentacji jest właśnie podzielona na te dwie części, związane z tymi metodami.

## PART I

### Slajd 11

Tak więc przejdźmy do części pierwszej: Meaning representation.

### Slajd 12

Zamysł metody konstruującej Meaning representation polega na 3 krokach: pobieramy dane w surowej formie (w tym przypadku jest to JSON). Następnie przy pomocy modelu językowego i odpowiedniego prompta przekształcamy wszystkie instancje na tekst natrualny, który tutaj będziemy nazywać tekstem referencyjnym. Na koniec jest pipeline, który również wykorzystuje model językowy i przekształca te teksty referencyjne w zbiór trójek semantycznych. Chciałbym teraz przejść do szczegółowego opisu tych kroków.

### Slajd 13

Po pierwsze potrzebujemy źródła danych. Wykorzystane zostało API o nazwie Quintd, które pozwala na proste pobranie różnych zbiorów danych z różnych źródeł, m.in w formacie JSON.

### Slajd 14

Następnie mając ten zbiór danych wykorzystujemy model językowy, który równolegle przy pomocy promptu przekształca surowe dane na tekst referencyjny.

### Slajd 15

Przeprowadzono ewaluację jakości tych tekstów względem danych źródłowych. Ocena była przeprowadzona na podstawie dwóch kryteriów: summary i faithfulness ocenianym od 1 do 5, gdzie 5 jest najlepszą oceną. Kryterium summary ocenia czy tekst jest zwięzłym i spójnym podsumowaniem ustrukturyzowanych danych i nie powtarza tych samych konceptów innymi słowami. Faithfulness ocenia czy fakty zawarte w tekście mają odniesienie do danych źródłowych (a więc czy nie ma halucynacji). Są dwie metody ewaluacyjne: ewaluacja automatyczna przy pomocu modelu językowego, oraz ewaluacja ludzka. Ewaluacja automatyczna oceniła summary i faithfulness niemalże perfekcyjnie dając wynik bliski 5. Ewaluacja ludzka zaś była surowsza, dając niższe noty, ale ich średnia i tak jest powyżej 4.

### Slajd 16

Przechodząc do kroku trzeciego, mając tekst referencyjny, chcemy go przekonwertować na trójki semantyczne. Do tego zostały zaproponowane i przetestowane 3 pipeline'y.

### Slajd 17

Pierwszy z pipeline'ów wykorzystuje model językowy do tego, żeby równolegle przy pomocy prompta przekształcić teksty na trójki. Jednakże taka prosta konwersja stawarza problem, że wśród zestawów trójek mogą powstać predykaty które znaczą dokładnie to samo, lecz zostały inaczej sformułowane. Dlatego po konwersji jest robiony dodatkowo krok normalizujący, który polega na ponownym wykorzystaniu modelu językowego do złączenia predykatów o tym samym znaczeniu.

### Slajd 18

Kolejny pipeline polega na stworzeniu tzw. blueprint'u, który zawiera informacje o tym jakich predykatów używać podczas konwersji, przykładowe trójki jakie można stworzyć z tych predykatów, przykładowe teksty, oraz dodatkowe porady. Blueprint tworzony jest w prociesie, który polega na wybieraniu losowego tekstu i sprawdzaniu czy da się ten blueprint zastosować. Jeśli nie to blueprint jest aktualizowany. Po tym procesie równolegle zostają przekształcone wszystkie teksty na trójki z wykorzystniem blueprint'u

### Slajd 19

Ostatni testowany pipeline polega na wykorzystaniu modelu językowego do iteracyjnego przekształcania tekstu referncyjnego na trójki, z pomocą "katalogu", który zawiera listę możliwych do użycia predykatów, wraz z przykłdowymi trójkami jak tego predykatu użyć. Jeśli przy pomocy aktualnego katalogu nie da się stworzyć trójek z tekstu, to katalog jest aktualizowany o potrzebne predykaty. Po wyczerpaniu ustalonej ilości iteracji, katalog jest uznawany za kompletny i reszta tekstów jest przekształcana na trójki równolegle.

### Slajd 20

Te pipeline'y zostały ocenione na dwóch kryteriach: additions i omissions. Additions ocenia czy znajdują się trójki, które nie mają odwołania w tekście referencyjnym, a omissions ocenia czy zabrakło jakichś trójek, które są w tekście referencyjnym. Tak samo jak wcześniej są dwie metody ewaluacji: ewaluacja automatyczna i ewaluacja ludzka. Najlepszą metodą okzała się być metoda Text-First extraction with Normalization, czyli ten najprostszy pipeline z normalizacją. Na drugim miejscu jest metoda z katalogiem, a na końcu metoda z blueprint'em. Ewaluacja automatyczna i ludzka jest zgodna co do tego w jakiej kolejności umieścić te metody od najlepszej do najgorszej. Metoda z normalizacją otrzymała niemalże perfekcyjne oceny zarówno od jednej ewaluacji jak i drugiej. Kolejne metody były oceniane bardziej przychylnie przez ewaluacje automatyczną, a przez ewaluację ludzką bardziej krytcznie. Nie pozostaje jednak wątpliowści, że metoda z normalizacją jest najlepszym pipelinem zarówno pod względem jakości jak i szybkości wykonania.

### Slajd 21

Powstała jeszcze druga, dodatkowa metoda. Polega ona na przeprowadzeniu fine-tuningu modelu językowego na danych, które powstały z jednego z pipeline'ów. Wytrenowany model ma za zadnie na podstawie surowych danych podanych w prompcie, stworzyć trójki semantyczne, wraz z tekstem referencyjnym.

### Slajd 22

Eksperymenty pokazują, że każda testowana konfiguracja hiperparametrów poprawia F1. Nie da się jednoznacznie wybrać najlepszej konfiguracji, ponieważ zależnie od kryterium na którym nam zależy, inna konfiguracja jest najlepsza. Patrząc na BLEU i METEOR najlepszą konfiguracją jest Low learning rate, a patrząc na F1 jest to Base config.

## PART II

### Slajd 23

To była pierwsza część pracy magisterki, teraz przechodzimy do drugiej części, którą jest Surface realization.

### Slajd 24

Zacznijmy od tego, że surface realization z trójek na tekst może być wykonany zwykłym promptem do modelu językowego. Otrzymamy wtedy płynnie brzmiący tekst ale nie jesteśmy w stanie wyjaśnić, dlaczego taki tekst właśnie powstał.

### Slajd 25

System z agentami wykorzystującymi modele językowe i tworzący program w Pythonie poprawia ten problem dając w pełni intepretowalny kod. Jednakże każdy agent działa niezależnie, przez co nie mają kontekstu całego problemu. Do tego nie da się tego procesu zrónoleglić

### Slajd 26

Dlatego w pracy magisterskiej zaproponowano zastąpienie systemu z agentami, algorytmem ewolucyjnym. Pomysł tworzenia programów w ten sposób został zaproponowany przez Google i nazywa się AlphaEvolve. Algorytm ten składa się z 4 elementów i każdy z nich musi zostać zdefiniowany przez człowieka. Najpierw musi zostać napisany ręcznie program początkowy, który będzie pierwszym elementem w bazie programów. Baza programów jest tutaj odpowiednikiem populacji. Kolejnym elementem jest ręcznie napisany prompt, który wyjaśni jaki jest rozwiązywany problem. Do tego prompta jest dołączany wybrany program, wraz z jego oceną i potencjalnymi wskazówkami co jest do poprawy. Wybór programu jest tutaj odpowiednikiem selekcji. Ten prompt jest wysyłany do wcześniej wybranego modelu językowego, który dokonuje odpowiednich modyfikacji na programie, co jest odpowiednikiem mutacji lub krzyżowania. Zmodyfikowany program jest poddawany ewaluacji, która też została wcześniej zdefiniowana co jest odpowiednikiem funkcji dopasowania. Ostatecznie program wraz z oceną trafia do populacji przy okazji usuwając programy z najgorszą oceną.

### Sladj 27

Tak więc dzięki temu mamy nowy system, który stworzy w pełni interpretowalny program w Pythonie

### Slajd 28

Przeprowadzono ewolucje z różnymi wariantami. Przetestowano wiariant w którym funkcją dopasowania jest obliczenie BLEU na podstawie wygenerowanego przez program tekstu i tekstów referencyjnych lub model językowy jako sędzia, który tak samo oceniał wygenerowany tekst z tekstem referencyjnym. Przetestowano też wariant z mutacjami lub krzyżowaniem, oraz wariant używający tylko jednego modelu prez całą ewolucję lub zestawu dwóch modelów, które były losowo wybierane w trakcie ewolucji.

### Slajd 29

Wyniki eksperymentów na zbiorze testowym pokazują, że AlphaEvolve działa lepiej niż system z agentami na każdym kryterium. Udało się osiągnąć znacznie lepszy wynik w gramatyczności, oraz przez LLM-as-a-judge oraz nie występują żadne adycje i omisjie. Na tych samych kryteriach AlphaEvolve jest lepszy niż zfine-tunowany BART, jednakżę patrząc na klasyczne metryki BLEU, BLEURT i METEOR pozostają lepsze. Porównując AlphaEvolve z zwykłym promptem do modelu językowego, widzimy, że prompt uzyskuje wyniki lepsze lub te same. Jednakże przewagą AlphaEvolve nad promptem jest to, że uzyskaliśmy w pełni interpretowalny Surface realization, którego inferencja jest szybsza i można ją wykonać na CPU.

### Slajd 30

Podsumowując, ta praca magisterska wnosi: trzy pipeline'y, które konstruują Meaning representation z surowych danych, zfine-tunowany model językowy, który dokonuje tej konstrukcji, algorytm ewolucyjny tworzący w pełni interpretowalny Surface realization, oraz testuje wszystkie te metody.

Dziękuję za uwagę.
