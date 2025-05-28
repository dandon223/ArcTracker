Database class diagram
======================

.. uml::

      @startuml
      
      'style options 
      skinparam monochrome true
      skinparam circledCharacterRadius 9
      skinparam circledCharacterFontSize 8
      skinparam classAttributeIconSize 0
      hide empty members

      enum CardSuit {
        ADMINISTRATION
        AGGRESSION
        CONSTRUCTION
        MOBILIZATION
      }

      enum CardNumber {
        ONE
        TWO
        THREE
        FOUR
        FIVE
        SIX
        SEVEN
      }

      enum CardsPlayedFaceDown {
        ZERO
        ONE
        TWO
      }

      class Card {
        - uuid: UUID
        + suit: CardSuit
        + number: CardNumber
      }

      class Player {
        - uuid: UUID
        + nick: string
        + created_time: Date
      }

      class Game {
        - uuid: UUID
        + name: string
        + created_time: Date
        + players: Player
        + cards_not_played: Card
        + finished: bool
      }

      Game "0..*" -- "2..4" Player
      Game "0..*" -- "0..*" Card

      class GameRound {
        - uuid: UUID
        - game: Game
        - chapter: Integer
        - round: Integer
      }

      GameRound "1..*" -- "1" Game

      class PlayerHand {
        - uuid: UUID
        + player: Player
        + game: Game
        + cards: Card
        + number_of_cards: int
      }

      PlayerHand "0..*" -- "1" Player
      PlayerHand "2..4" -- "1" Game
      PlayerHand "0..*" -- "0..*" Card

      class CardPlayedInRound {
        - uuid: UUID
        + player: Player
        + game_round: GameRound
        + card_face_up: Card
        + number_of_cards_face_down: CardsPlayedFaceDown
      }

      CardPlayedInRound "0..*" -- "1" Player
      CardPlayedInRound "0..*" -- "1" GameRound
      CardPlayedInRound "0..*" -- "0..1" Card

      @enduml