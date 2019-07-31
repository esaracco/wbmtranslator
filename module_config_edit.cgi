#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $lang = $in{'t'};
my @sfile_ref = ();
my %file = ();
my $fref = '';
my $lref = '';
my @updated = ();
my $filter_modified = defined ($in{'filter_modified'});

if (-f &trans_get_path ($app, "config.info.$ref_lang"))
{
  $fref = "config.info.$ref_lang";
  $lref = ".$ref_lang";
}
else
{
  $fref = "config.info";
  $lref = '';
}
$fref = (-f &trans_get_path ($app, "config.info.$ref_lang")) ?
  "config.info.$ref_lang" : 'config.info';

@sfile_ref = &trans_get_items_static (&trans_get_path ($app, $fref));
%file = &trans_get_items ((&trans_get_path ($app, 'config.info')) . 
  (($ref_lang eq $lang) ? $lref : ".$lang"));
@updated = &trans_get_array_updated ( 'config', $ref_lang, $app);

##### POST actions #####
#
# Update config.info file
if (defined ($in{'update'}))
{
  my $old = (&trans_get_path ($app, 'config.info')) . 
    (($ref_lang eq $lang) ? $lref : ".$lang");
  
  open (H, '>', $old);
  chmod (0644, $old);
  foreach my $i (@sfile_ref)
  {
    my ($k, $v) = each (%$i);

    print H "$k=".$in{$k}."\n" if ($in{$k} ne '');
  }
  close (H);

  &trans_char2ent ($old, 'html');

  &redirect ("module_config_main.cgi?app=$app&t=$lang&o=update_trans");
  exit;
}
#
########################

&trans_header ($text{'EDIT_TITLE'}, $app, $lang);
print qq(<br/>);
if ($ref_lang ne $lang)
{
  printf qq($text{'EDIT_DESCRIPTION1'}), $fref, $lang;
}
else
{
  printf qq($text{'EDIT_DESCRIPTION2'}), $fref, $lang;
}

print qq(<p/>);
print qq(<form action="module_config_edit.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);

print qq(<div class="btn-group"><button type="submit" class="btn btn-default btn-tiny ui_form_end_submit" name="filter_modified"><i class="fa fa-fw fa-filter"></i> <span>$text{'ONLY_MODIFIED'}</span></button>&nbsp;<button type="submit" class="btn btn-default btn-tiny ui_form_end_submit"><i class="fa fa-fw fa-filter"></i> <span>$text{'DISPLAY_ALL'}</span></button></div>);

print qq(
  <p/><div style="text-align:center">
    <span class="circle success"></span> = $text{'TRANSLATED'},
    <span class="circle error"></span> = $text{'NOT_TRANSLATED'},
    <span class="circle warning"></span> = $text{'MODIFIED'}
  </div>
);

print qq(<p/><table class="trans keys-values" width="100%">);
foreach my $i (@sfile_ref)
{
  my ($k, $v) = %$i;
  my $trans_value = ($in{$k} ne '') ? $in{$k} : $file{$k};
  my %hash = &trans_get_item_updated (\@updated, $k);
  my $modified = ($hash{'key'} eq $k); 
  my $panel = '';

  # Not translated
  if ($trans_value eq '')
  {
    $panel = sprintf (qq(<tr><td><span class="circle error"></span>&nbsp;$k:</td><td class="to-translate">%s</td></tr>), &html_escape($v));
  }
  # Modified
  elsif ($modified)
  {
    $panel = qq(<tr><td><span class="circle warning"></span>&nbsp;$k:</td><td></td></tr>);
    $panel .= qq(<tr><td></td>);
  
    $panel .= sprintf (qq(<td>
        <table class="trans keys-values" width="100%">
          <tr>
            <td nowrap><b>$text{'OLD_STRING'}:</b></td>
            <td class="to-translate" style="background:#ffff77">%s</td>
          </tr>), &html_escape($hash{'old'}));

    if ($ref_lang ne $lang)
    {
      $panel .= sprintf (qq(
        <tr>
          <td nowrap><b>$text{'NEW_STRING'}:</b></td>
          <td class="to-translate" style="background:#aaffaa">%s</td>
       </tr>), &html_escape($hash{'new'}));
    }

    $panel .= qq(</table></td></tr>);
  }
  # Translated
  else
  {
    $panel = sprintf (qq(<tr><td><span class="circle success"></span>&nbsp;$k:</td><td class="to-translate">%s</td></tr>), &html_escape($v));
  };
  
  if ($filter_modified && !$modified) 
  {
    print qq(<input type="hidden" name="$k" value=");
    print &html_escape ($trans_value);
    print qq(">);
  }
  else
  {
    printf qq(
      $panel
      <tr>
        <td></td>
        <td><textarea name="$k" rows=5>$trans_value</textarea></td>
      </tr>);
  }
}
print qq(</table>);
print qq(<p/><div><button type="submit" name="update" class="btn btn-success ui_form_end_submit"><i class="fa fa-fw fa-check-circle-o"></i> <span>$text{'UPDATE_TRANSLATION_FILE'}</span></button></div>);
print qq(</form>);

&trans_footer("module_config_main.cgi?app=$app", $text{'MODULE_CONFIG_INDEX'});
