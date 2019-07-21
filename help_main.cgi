#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $old_app = $in{'old_app'};
my $app_print = &urlize ($app);
my $monitor = $in{'monitor'};

if ($old_app eq $app)
{
  &trans_set_user_var ("monitor_" . &trans_get_current_app () . "_$app",
    $monitor);
}

# my_get_msg ()
# IN: -
# OUT: the message to display or ''
#
# return a state message if a action occured
# 
sub my_get_msg ()
{
  my $ret = '';

  # updated a help file
  if ($in{'o'} eq 'update_trans')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_UPDATED_TRANSLATION'}</b></p>), 
      $in{'t'};
  }
  
  return $ret;
}

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "help", 1, 0);
print "<hr>\n";

# print javascript section
print qq(
  <script language="javascript">
  function go_to (f1, fname)
  {
    eval ('f2 = document.forms[0].' + fname + '.value');
    document.location.href = 
      'help_edit.cgi?app=$app' + 
      '&f1=' + escape (f1) + 
      '&f2=' + escape (f2);
  }
  </script>
);

printf qq(<h1>$text{'HELP_TITLE'}</h1>), $app;
&trans_get_menu_icons_panel ('help_main', $app);
print qq(<p>$text{'HELP_DESCRIPTION1'}</p>);

print qq(<p>);
print qq(<form action="help_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);
print qq(<input type="hidden" name="radio_select" value="">);
print qq(<select name="app" onChange="submit()">);
printf qq(<option value="">$text{'SELECT_MODULE'}</option>\n);
&trans_modules_list_get_options ([$app], '');
print "</select>";

print qq(<input type="submit" value="$text{'REFRESH'}">);

&trans_monitor_panel ($app) if ($app ne '');

# display state message
print &my_get_msg ();

# if a module have been chosen
if ($app ne '')
{
  my $path = &trans_get_path ($app, 'help');
  my $form_name = 0;
  my @files = ();

  # retrieve all files for this module
  opendir (DH, $path);
  foreach my $item (readdir (DH))
  {
    push (@files, $item) if ($item =~ /^[^\.]+.html$/);
  }
  closedir (DH);
 
  if (@files)
  {
    my @lang_array = &trans_get_existing_translations ([$app]);

    print qq(<p>$text{'HELP_DESCRIPTION2'}</p>);

    # display translation table for the selected module
    print qq(<p>);
    print qq(<table border="0" cellspacing="2" cellpadding="2">);
    print qq(
      <tr>
        <th $tb>$text{'STATE'}</th>
        <th $tb>$text{'FILE'}</th>
        <th $tb>$text{'SIZE'}</th>
        <th $tb>$text{'MODIFIED'}</th>
        <th $tb>$text{'TRANSLATIONS'}</th>
        <th $tb>$text{'TO_TRANSLATE'}</th>
        <th $tb>$text{'TO_UPDATE'}</th>
        <th $tb>$text{'ACTION'}</th>
      </tr>
    );

    foreach my $key (sort (@files))
    {
      my ($size, $modified) = (stat ("$path/$key"))[7,9];
      my $to_translate = 0;
      my $not_translated = 0;
      my $state_icon = '';

      my $line = sprintf qq(
                   <td>%s</td>
                   <td>%s</td>
                   <td>%s</td>
                   <td><select name="select_file$form_name">
                 ),
                 $key,
                 &trans_get_string_from_size ($size),
                 strftime ("%Y-%m-%d", localtime ($modified));

      foreach my $item (@lang_array)
      {
        next if ($item eq $reg_lang || !&trans_is_language ($item));
        my $file = '';
	my $state= '';
	my $size1 = 0;
	my $modified1 = '';

        $key =~ /^(.*)\.htm/;
        $file = "$1.$item.html";
        ($size1, $modified1) = (stat ("$path/$file"))[7,9];
	
	if ((! -f "$path/$file") || (!$size1))
	{
          $state = '[!] - ';
	  $not_translated++;
	}
	else
	{
	  if (Date_Cmp (
                strftime ("%Y-%m-%d", localtime ($modified1)), 
                strftime ("%Y-%m-%d", localtime ($modified))) < 0)
	  {
	    $state = '[X] - ';
	    ++$to_translate;
	  };

        }
        $line .= sprintf (qq(<option value="$file"%s>$state$file</option>\n),
                         ($item eq $current_lang) ? 'selected="selected"':'');
      }

      $line .= sprintf qq(
                 </select></td>
                 <td>%s</td>
                 <td>%s</td>
                 <td align="center"><a href="javascript:go_to('$key', 'select_file$form_name')"><img src="images/edit.png" alt="$text{'EDIT'}" title="$text{'EDIT_SELECTION'}" border=0></a></td>
                 </tr>
               ),
              ($not_translated == 0) ?
                qq(<img src="images/ok.png">) :
                qq(<img src="images/bad.png"> $not_translated),
              ($to_translate == 0) ?
                qq(<img src="images/ok.png">) :
                qq(<img src="images/bad.png"> $to_translate);

              $state_icon =
                (!$to_translate && !$not_translated) ?
                  qq(<img src="images/smiley_ok.png" alt="$text{'GOOD'}"
                     title="$text{'GOOD'}">) :
                  ($to_translate && $not_translated) ?
                    qq(<img src="images/smiley_bad.png" alt="$text{'BAD'}"
                       title="$text{'BAD'}">) :
                    qq(<img src="images/smiley_notbad.png"
                       alt="$text{'NOT_SO_BAD'}" title="$text{'NOT_SO_BAD'}">);
      
      $line = "<tr $cb><td>$state_icon</td>$line";
      print $line;

      ++$form_name;
    }
    print qq(</table>);
    print qq(<p><font size="-1">$text{'HELP_LEGEND'}</font></p>);
    print qq(</p>);
  }
  else
  {
    print "<p><b>$text{'HELP_NOEXIST'}</b></p>";
  }
}
print qq(</form>);
print qq(</p>);

print qq(<hr/>);
&footer ('', $text{'MODULE_INDEX'});
