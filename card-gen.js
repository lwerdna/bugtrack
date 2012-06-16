// Draw a BugTrack player card
function drawCard(color,player,container,rank,rating,rd,wins,losses,streak) {

  var c_width  = 350;   // Card width
  var c_height = 150;   // Card height
  var c_border = 10;    // Card border from canvas
  var c_edge   = 15;    // Card border corner softness

  var s_x       = 40
  var s_x_tab   = 60
  var s_y       = 60
  var s_y_tab   = 20

  var c_fill    = "#fff";
  if (color == 'b') {
    c_fill = "#aaa";
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
  var title = paper.text(25,35,player);
  title.attr({'text-anchor': 'start', 'font-size':25, 'font-family':'stencil'});

  var yi = 0;

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Rank');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var val_01  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,rank);
  val_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Rating');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var val_01  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,rating + ' (' + rd + ')');
  val_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Record');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var val_01  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,'[' + wins + '-' + losses + ']');
  val_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});

  var stat_01 = paper.text(s_x + s_x_tab * 0,s_y + s_y_tab * yi,'Streak');
  stat_01.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'aharoni'});
  var streak_str = '';
  if (streak > 0) {
      streak_str = streak + ' '
      if (streak == 1) {
        streak_str += 'Win';
      } else {
        streak_str += 'Wins';
      }
  } else {
      streak_str = (streak * -1) + ' '
      if (streak == -1) {
        streak_str += 'Loss';
      } else {
        streak_str += 'Losses';
      }
  }
  var val_02  = paper.text(s_x + s_x_tab * 1,s_y + s_y_tab * yi++,streak_str);
  val_02.attr({'text-anchor': 'start', 'font-size':15, 'font-family':'consolas'});
}
