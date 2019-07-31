#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
my $app = $in{'app'};
my $old_app = $in{'old_app'};
my $app_print = &urlize ($app);
my @files = ();
my $path = &trans_get_path ($app, 'help');

# retrieve all files for this module
if ($app ne '')
{
  opendir (DH, $path);
  foreach my $item (readdir (DH))
  {
    push (@files, $item) if ($item =~ /^[^\.]+.html$/);
  }
  closedir (DH);
}

# init_msg ()
#
# Set success or error message.
# 
sub init_msg ()
{
  # Updated a help file
  if ($in{'o'} eq 'update_trans')
  {
    $_success = sprintf ($text{'MSG_UPDATED_TRANSLATION'}, $in{'t'});
  }
}

&trans_header ($text{'HELP_TITLE'}, $app);
&trans_get_menu_icons_panel ('help_main', $app);
print qq(<br>$text{'HELP_DESCRIPTION1'});

#FIXME
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

print qq(<p>);
print qq(<form action="help_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);
print qq(<input type="hidden" name="radio_select" value="">);

&trans_modules_list_get_options ([$app], '');

if (@files && (my $msg = &trans_monitor_panel ($app, $in{'monitor'})))
{
  $_success = $msg;
}

# Set success or error msg
&init_msg ();

# if a module have been chosen
if ($app ne '')
{
  my $form_name = 0;

  if (@files)
  {
    my @lang_array = &trans_get_existing_translations ([$app]);

    print qq(<p>$text{'HELP_DESCRIPTION2'}</p>);

    # display translation table for the selected module
    print qq(<p>);
    print qq(<table class="trans header" width="100%">);
    print qq(
      <tr>
        <td>$text{'STATE'}</td>
        <td>$text{'FILE'}</td>
        <td>$text{'SIZE'}</td>
        <td>$text{'MODIFIED'}</td>
        <td>$text{'TRANSLATIONS'}</td>
        <td>$text{'TO_TRANSLATE'}</td>
        <td>$text{'TO_UPDATE'}</td>
        <td>$text{'ACTION'}</td>
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
                   <td align=center>%s</td>
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
                 <td align="center"><a href="javascript:go_to('$key', 'select_file$form_name')"><img src="images/edit.png" alt="$text{'EDIT'}" title="$text{'EDIT_SELECTION'}"></a></td>
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
      
      $line = "<tr><td align=center>$state_icon</td>$line";
      print $line;

      ++$form_name;
    }
    print qq(</table>);
    print qq(<p><font size="-1">$text{'HELP_LEGEND'}</font></p>);
    print qq(</p>);
  }
  else
  {
    $_error = $text{'HELP_NOEXIST'};
  }
}
print qq(</form>);
print qq(</p>);

&trans_footer ('', $text{'MODULE_INDEX'}, $_success, $_error, $_info);
