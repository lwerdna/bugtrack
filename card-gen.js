// Draw a BugTrack player card
function drawCard(playerName,container) {

  var c_width  = 350;   // Card width
  var c_height = 150;   // Card height
  var c_border = 10;    // Card border from canvas
  var c_edge   = 10;    // Card border corner softness

  var s_x       = 40
  var s_x_tab   = 60
  var s_y       = 60
  var s_y_tab   = 20

  var c_fill    = "#fff";
  if (container[1] == 'B') {
    c_fill = "#aaa";
  }
        
  // Collect player information
  var resp = ajax('cgi/jsIface.py?op=getcardstats&player=' + playerName)
  var lines = resp.split("\n")
  for(var j in lines) {
    var m = lines[j].match(/^(.*),(.*),(.*),(.*),(.*),(.*)$/);

    if(m) {
        playerRating = parseInt(m[1])
        playerRd     = parseInt(m[2])
        playerRank   = parseInt(m[3])
        playerWins   = parseInt(m[4])
        playerLosses = parseInt(m[5])
        playerStreak = parseInt(m[6])
    }
  }

  var paper = Raphael(document.getElementById(container), c_width, c_height);

  // Card background
  var card = paper.rect(c_border, 
                        c_border, 
                        c_width - 2 * c_border, 
                        c_height - 2 * c_border, 
                        c_edge); 
  card.attr({fill:c_fill, stroke: '#000',  'stroke-width': 2});

  // Player title and stats
  var title = paper.text(25,35,playerName);
  title.attr({'text-anchor': 'start', 'font-size':25, 'font-family':'stencil'});

  var yi = 0;

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Rank');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var val_01  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,playerRank);
  val_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Rating');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var val_01  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,playerRating + ' (' + playerRd + ')');
  val_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Record');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var val_01  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,'[' + playerWins + '-' + playerLosses + ']');
  val_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Streak');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var streak_str = '';
  if (playerStreak > 0) {
      streak_str = playerStreak + ' Win'
      if (playerStreak >= 1) {
        streak_str += 's';
      }
  } else {
      streak_str = (playerStreak * -1) + ' Loss'
      if (playerStreak <= -1) {
        streak_str += 'es';
      }
  }
  var val_02  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,streak_str);
  val_02.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});
}
