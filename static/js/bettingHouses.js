const bettingHouses = [
    "Selecione",
    "Bet365",
    "Betway",
    "1xBet",
    "Unibet",
    "William Hill",
    "Betsson",
    "Bwin",
    "Sportingbet",
    "888Sport",
    "Marathonbet",
    "Pinnacle",
    "SBOBET",
    "10Bet",
    "Dafabet",
    "Bet-at-home",
    "Interwetten",
    "LeoVegas Sports",
    "Royal Panda",
    "22Bet",
    "Betfair",
    "Coral",
    "Ladbrokes",
    "BetVictor",
    "Karamba Sports",
    "Mr Green",
    "Betfred",
    "Sky Bet",
    "Tipico",
    "Rizk Sports",
    "Guts Sports",
    "ComeOn!",
    "EnergyBet",
    "BetHard",
    "TonyBet",
    "MoPlay",
    "MansionBet",
    "Betbull",
    "BetStars",
    "Mobilebet",
    "Redbet Sports",
    "Fun88",
    "32Red Sport",
    "Genting Bet",
    "STSbet",
    "Vbet",
    "SportNation",
    "BoyleSports",
    "SpreadEx",
    "Betdaq",
    "QuinnBet",
    "Betano",
    "Stake",
];

$(document).ready(function() {
    $('#betting_house').select2({
        data: bettingHouses.map(function(betHouse) {
            return { id: betHouse, text: betHouse };
        }),
        placeholder: "Selecione a casa de aposta",
        allowClear: true
    });
});