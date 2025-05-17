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

      class Card {
        - suit: CardSuit
        - number: CardNumber
      }

      class Player {
        - uuid: UUID
        + nick: string
        + create_time: Date
      }

      class Game {
        - uuid: UUID
        + name: string
        + create_time: Date
        + finished: bool
      }

      class PlayerInGame {
        - player_uuid: Player.uuid
        - game_uuid: Game.uuid
      }

      Player "1" -- "*" PlayerInGame
      Game "1" -- "*" PlayerInGame

      class CardsPlayedInGame {
        - player_uuid: PlayerInGame.uuid
        - game_uuid: PlayerInGame.uuid
        + round_played: Integer
        + card_suit_played: Card.suit
        + card_number_played: Card.number
        + card_face_down: bool
      }

      CardsPlayedInGame "*" -- "1" Card
      CardsPlayedInGame "1" -- "1" PlayerInGame
      @enduml