My TF2 config

#General notes

The aspect ratio for fov maximum gain is 1.85:1

Calculate [here](http://www.rjdown.co.uk/projects/bfbc2/fovcalculator.php)

#Fetching dependencies

    $ git submodule init
    $ git submodule update

#Script style

##Symbol table

|Symbol|Meaning                           |Placement|
|:--   |:--                               |:--      |
|.     |condition separator               |between  |
|_     |sub-variable                      |between  |
|+     |true / enabled                    |before   |
|-     |false / disabled                  |before   |
|!     |toggle                            |before   |
|~     |reset                             |before   |
|$     |sync (invoke current)             |before   |
|?     |check                             |after    |
|++    |increment / next                  |either   |
|--    |decrement / previous              |either   |
|[i]   |list access to index or pointer   |after    |

More ideas:

|Symbol|Meaning                           |Placement|
|*     |pointer                           |before   |
|@     |method                            |before   |
|#     |captions                          |         |
|/     |extends (alias @do "@do/a; @do/b")|         |
|&     |address                           |         |

##Conditions

Condition separators should delegate to their parent

#Sounds

0 byte files work everywhere, but spam the console

#Surfaceproperties

These files were taken from `/hl2/scripts/` and `/tf/scripts/`
All gamematerial instances (other than "X") were replaced with the following:
    "gamematerial"	"I"

#Custom crosshairs

Access in the following manner:

    cl_crosshair_file "../replay/thumbnails/custom"